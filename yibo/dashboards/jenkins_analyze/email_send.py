from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
from email.utils import parseaddr
import smtplib

def write_log(msg):
    with open('/tmp/analyze.log', 'a') as fd:
        fd.write(msg)

def login_email(mail_host='200.200.0.11', mail_port='25'):
    server = None
    try:
        server = smtplib.SMTP(timeout=20)
        server.set_debuglevel(1)
        server.connect(mail_host, mail_port)
    except Exception as ex:
        write_log("connect email host failed! ex = %s" % ex)
        raise

    return server

def format_addr(s):
    """format addr

    :param s:
    :return:
    """

    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr.encode('utf-8')
                       if isinstance(addr, unicode) else addr))

def send_plain_email(mail_host='200.200.0.11', mail_port='25',
                     mail_from="90503@sangfor,com", mailto_list=[], sub = "",
                     msg=""):

    server = login_email(mail_host=mail_host, mail_port=mail_port)

    me = "from sangfor cloud <" + mail_from + ">"
    msg_text = MIMEText(msg, _subtype='plain', _charset='utf-8')
    msg_text['Subject'] = Header(sub, 'utf-8').encode()
    msg_text['From'] = format_addr(me)
    msg_text['To'] = ";".join(mailto_list)

    try:
        server.sendmail(mail_from, mailto_list, msg_text.as_string())
    except Exception as ex:
        write_log("send email failed! err = %s" % ex)
        raise
    finally:
        server.quit()

def send_html_email(mail_host='200.200.0.11', mail_port='25',
                     mail_from="90503@sangfor,com", mailto_list=[], sub = "",
                     msg=""):
    server = login_email(mail_host=mail_host, mail_port=mail_port)

    me = "from sangfor cloud <" + mail_from + ">"
    msg_text = MIMEText(msg, _subtype='html', _charset='utf-8')
    msg_text['Subject'] = Header(sub, 'utf-8').encode()
    msg_text['From'] = format_addr(me)
    msg_text['To'] = ";".join(mailto_list)

    try:
        server.sendmail(mail_from, mailto_list, msg_text.as_string())
    except Exception as ex:
        write_log("send email failed! err = %s" % ex)
        raise
    finally:
        server.quit()


