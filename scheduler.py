# scheduler.py
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import sys
from datetime import datetime

# 导入配置
from config import (
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, RECIPIENT_EMAIL,
    EMAIL_SEND_TIME, MATCHED_JOBS_SUMMARY_PATH
)

# 导入主流程
from main import run_job_agent_pipeline

def send_email(subject, body_html, to_email):
    """
    通过SMTP发送邮件
    :param subject: 邮件主题
    :param body_html: 邮件正文 (HTML格式)
    :param to_email: 收件人邮箱地址
    """
    print(f"正在准备发送邮件至 {to_email}...")
    
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject

    # 添加HTML正文
    msg.attach(MIMEText(body_html, 'html', 'utf-8'))

    try:
        # 根据端口判断使用SSL还是TLS
        # 465端口通常用于SSL，587端口通常用于TLS
        if SMTP_PORT == 465:
            print(f"尝试使用SSL连接到 {SMTP_SERVER}:{SMTP_PORT}...")
            # 使用SMTP_SSL，它会自动处理SSL握手，不需要再调用starttls()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.set_debuglevel(1)  # 打印调试信息
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            print(f"尝试使用TLS连接到 {SMTP_SERVER}:{SMTP_PORT}...")
            # 使用标准的SMTP，然后手动升级到TLS
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.set_debuglevel(1)  # 打印调试信息
                server.starttls()  # 启用安全传输模式
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
        
        print(f"邮件已成功发送至 {to_email}。")
        return True

    except smtplib.SMTPAuthenticationError:
        print("SMTP认证失败，请检查用户名和密码（或应用专用密码）。")
        print("提示：请确保您在.env文件中使用的是邮箱服务商提供的'应用专用密码'，而不是您的登录密码。")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"无法连接到SMTP服务器 {SMTP_SERVER}:{SMTP_PORT}，请检查服务器地址、端口或网络连接。错误详情: {e}")
        return False
    except smtplib.SMTPServerDisconnected:
        print("SMTP服务器在操作过程中意外断开连接。这通常是由于服务器端的安全策略阻止了脚本登录。")
        print("建议解决方案：")
        print("1. 确保您使用的是'应用专用密码'。")
        print("2. 对于Gmail用户，尝试在账户设置中开启'不够安全的应用的访问权限'。")
        print("3. 检查邮箱服务商是否有关于此登录尝试的安全警报，并按照指引操作。")
        return False
    except smtplib.SMTPException as e:
        # 打印更详细的SMTP错误信息
        print(f"发送邮件时发生SMTP错误: {e}")
        # 尝试获取更具体的错误码和信息
        if hasattr(e, 'smtp_code') and hasattr(e, 'smtp_error'):
            error_detail = e.smtp_error
            if isinstance(error_detail, bytes):
                try:
                    error_detail = error_detail.decode('utf-8')
                except UnicodeDecodeError:
                    error_detail = error_detail.decode('latin-1', errors='ignore')
            print(f"SMTP错误码: {e.smtp_code}, 错误详情: {error_detail}")
        return False
    except Exception as e:
        print(f"发送邮件时发生未知错误: {e}")
        return False

def job_to_html(job):
    """将单个职位信息转换为HTML表格行"""
    return f"""
    <tr>
        <td style="border: 1px solid #ddd; padding: 8px;"><a href="{job.get('url', '#')}" target="_blank">{job.get('title', 'N/A')}</a></td>
        <td style="border: 1px solid #ddd; padding: 8px;">{job.get('company', 'N/A')}</td>
        <td style="border: 1px solid #ddd; padding: 8px;">{job.get('source', 'N/A')}</td>
        <td style="border: 1px solid #ddd; padding: 8px;">{job.get('reason', 'N/A').replace(chr(10), '<br>')}</td>
    </tr>
    """

def send_daily_job_report():
    """
    定时任务：执行数据抓取和处理，然后读取匹配结果并发送邮件
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ====== 定时任务触发：开始执行完整流程 ======")
    
    # 1. 执行数据抓取和处理流水线
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 1/3] 正在调用 main.py 的数据抓取和处理流水线...")
    try:
        run_job_agent_pipeline()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 1/3] 数据抓取和处理流水线执行成功。")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 1/3] 错误：数据抓取和处理流水线执行失败: {e}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ====== 定时任务因流水线失败而中止 ======")
        # 如果流水线失败，则不继续发送邮件
        return

    # 2. 检查并读取新生成的匹配结果文件
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 2/3] 正在检查匹配结果文件: {MATCHED_JOBS_SUMMARY_PATH}...")
    if not os.path.exists(MATCHED_JOBS_SUMMARY_PATH):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 2/3] 错误：匹配结果文件未找到: {MATCHED_JOBS_SUMMARY_PATH}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ====== 定时任务因文件未找到而中止 ======")
        return

    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 2/3] 成功找到文件，正在读取和解析JSON...")
        # 使用 errors='replace' 来处理文件中可能存在的非UTF-8编码字符，防止解码失败
        with open(MATCHED_JOBS_SUMMARY_PATH, 'r', encoding='utf-8', errors='replace') as f:
            report_data = json.load(f)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 2/3] JSON文件解析成功。")
    except json.JSONDecodeError as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 2/3] 错误：解析匹配结果文件失败: {e}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ====== 定时任务因JSON解析失败而中止 ======")
        return
    except FileNotFoundError:
        # 这个理论上不会发生，因为前面已经检查过 os.path.exists
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 2/3] 错误：匹配结果文件未找到: {MATCHED_JOBS_SUMMARY_PATH}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ====== 定时任务因文件未找到而中止 ======")
        return
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 2/3] 错误：读取匹配结果文件时发生未知错误: {e}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ====== 定时任务因文件读取错误而中止 ======")
        return

    summary = report_data.get("summary", "无总结信息。")
    matched_jobs = report_data.get("matched_jobs", [])
    other_jobs = report_data.get("other_jobs", []) # 新增：获取其他岗位
    timestamp = report_data.get("timestamp", "未知时间")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 2/3] 数据摘要：核心匹配 {len(matched_jobs)} 个，其他关注 {len(other_jobs)} 个。")
    
    # 邮件主题
    subject = f"您的每日职位匹配报告 - {datetime.now().strftime('%Y-%m-%d')}"

    # 邮件正文 (HTML格式)
    html_body = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2>您好，这是您的每日职位匹配报告</h2>
        <p><strong>报告生成时间:</strong> {timestamp}</p>
        
        <h3>市场汇总与分析</h3>
        <p>{summary.replace(chr(10), '<br>')}</p>
        
        <h3>核心匹配职位</h3>
    """
    
    if matched_jobs:
        html_body += """
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead style="background-color: #e6f7ff; /* 轻微不同的背景色区分 */
                <tr>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">职位名称</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">公司</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">来源</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">推荐理由</th>
                </tr>
            </thead>
            <tbody>
        """
        for job in matched_jobs:
            html_body += job_to_html(job)
        html_body += """
            </tbody>
        </table>
        """
    else:
        html_body += "<p>今日暂无核心匹配的职位。</p>"

    # 新增：其他值得关注职位部分
    html_body += "<br><h3>其他值得关注职位</h3>"
    if other_jobs:
        html_body += """
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead style="background-color: #f0f0f0; /* 另一种背景色区分 */
                <tr>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">职位名称</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">公司</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">来源</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">推荐理由</th>
                </tr>
            </thead>
            <tbody>
        """
        for job in other_jobs:
            html_body += job_to_html(job) # 复用同一个HTML生成函数
        html_body += """
            </tbody>
        </table>
        """
    else:
        html_body += "<p>今日暂无其他特别值得关注的职位。</p>"
        
    html_body += """
        <br>
        <p style="color: #888; font-size: 0.9em;">此邮件由AI求职代理自动发送。</p>
    </body>
    </html>
    """

    # 发送邮件至配置的收件人
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [步骤 3/3] 正在准备发送邮件...")
    send_email(subject, html_body, RECIPIENT_EMAIL)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ====== 定时任务流程执行完毕 ======")


def main_scheduler_loop():
    """
    主循环，用于运行定时任务
    """
    print("定时任务调度器已启动...")
    print(f"邮件发送时间已设置为每天: {EMAIL_SEND_TIME}")
    print("按 Ctrl+C 退出。")
    print("调度器正在等待下一个执行周期...")

    # 安排每天的任务
    schedule.every().day.at(EMAIL_SEND_TIME).do(send_daily_job_report)

    try:
        while True:
            # 在每次检查前打印当前时间，方便调试
            # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 调度器心跳: 检查待执行任务...", end='\\r') # \\r 会覆盖上一行，比较整洁
            schedule.run_pending()
            time.sleep(1) # 每秒检查一次
    except KeyboardInterrupt:
        print("\\n定时任务调度器已停止。")
        sys.exit(0)

if __name__ == "__main__":
    main_scheduler_loop()