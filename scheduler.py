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
        # 连接SMTP服务器并发送邮件
        # 使用 with 语句确保连接被正确关闭
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # 启用安全传输模式
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"邮件已成功发送至 {to_email}。")
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP认证失败，请检查用户名和密码（或应用专用密码）。")
        return False
    except smtplib.SMTPConnectError:
        print(f"无法连接到SMTP服务器 {SMTP_SERVER}:{SMTP_PORT}，请检查服务器地址和端口。")
        return False
    except smtplib.SMTPException as e:
        print(f"发送邮件时发生SMTP错误: {e}")
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
    定时任务：读取匹配结果并发送邮件
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行定时任务：发送每日职位报告...")
    
    if not os.path.exists(MATCHED_JOBS_SUMMARY_PATH):
        print(f"错误：匹配结果文件未找到: {MATCHED_JOBS_SUMMARY_PATH}")
        return

    try:
        with open(MATCHED_JOBS_SUMMARY_PATH, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"错误：解析匹配结果文件失败: {e}")
        return
    except Exception as e:
        print(f"错误：读取匹配结果文件时发生未知错误: {e}")
        return

    summary = report_data.get("summary", "无总结信息。")
    matched_jobs = report_data.get("matched_jobs", [])
    other_jobs = report_data.get("other_jobs", []) # 新增：获取其他岗位
    timestamp = report_data.get("timestamp", "未知时间")
    
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
    send_email(subject, html_body, RECIPIENT_EMAIL)


def main_scheduler_loop():
    """
    主循环，用于运行定时任务
    """
    print("定时任务调度器已启动...")
    print(f"邮件发送时间已设置为每天: {EMAIL_SEND_TIME}")
    print("按 Ctrl+C 退出。")

    # 安排每天的任务
    # schedule.every().day.at(EMAIL_SEND_TIME).do(send_daily_job_report)
    # 为了测试，可以先用每分钟执行一次
    schedule.every(1).minutes.do(send_daily_job_report) # 测试用，每分钟发送一次
    # 正式使用时，请注释掉上一行，并取消注释下一行
    # schedule.every().day.at(EMAIL_SEND_TIME).do(send_daily_job_report)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n定时任务调度器已停止。")
        sys.exit(0)

if __name__ == "__main__":
    # 在启动调度器前，可以先手动运行一次main.py以确保数据是最新的
    # 或者可以设计成调度器在发送邮件前先调用main.py的流程
    print("在启动调度器前，是否先运行一次数据抓取和处理流程？(y/n)")
    # choice = input("> ").strip().lower()
    choice = 'y' # 为了自动化，暂时默认为y
    if choice == 'y':
        print("正在执行数据抓取和处理流程...")
        # 需要确保main.py在同一个目录下，或者通过模块方式调用
        # 这里简单使用exec，但更推荐将main.py的逻辑封装成函数后导入调用
        try:
            # 假设main.py和scheduler.py在同一目录
            # 这种方式不是最佳实践，最佳实践是将main.py的逻辑封装成函数
            # from main import run_job_agent_pipeline
            # run_job_agent_pipeline()
            # 为了简单起见，这里使用subprocess或直接exec
            import subprocess
            import sys
            
            # 获取当前脚本所在的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            main_py_path = os.path.join(current_dir, 'main.py')
            
            print(f"正在执行: {main_py_path}")
            # 使用 errors='replace' 来处理无法解码的字符，避免程序崩溃
            result = subprocess.run([sys.executable, main_py_path], capture_output=True, text=True, encoding='utf-8', errors='replace')
            
            if result.returncode == 0:
                print("数据抓取和处理流程执行成功。")
                if result.stdout:
                    print("标准输出:\n", result.stdout)
            else:
                print("数据抓取和处理流程执行失败。")
                if result.stderr:
                    print("标准错误:\n", result.stderr)
        except Exception as e:
            print(f"调用main.py时出错: {e}")

    main_scheduler_loop()