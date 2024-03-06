import json5


def get_config():
    # 读取JSON文件
    with open('config.json5', 'r', encoding='utf-8') as file:
        config = json5.load(file)

    # 从JSON对象中提取信息并赋值给变量
    uid = config['uid']
    cookie = config['cookie']
    uploadTimeInterval = config['uploadTimeInterval']
    sleeptime = config['sleeptime']
    interval = config['interval']
    rule1_user = config['rule1']['user']
    rule1_user_other = config['rule1']['user_other']
    rule1_start = config['rule1']['start']
    rule1_hours = config['rule1']['hours']
    rule1_promotion = config['rule1']['promotion']
    rule1_ur = config['rule1']['ur']
    rule1_dr = config['rule1']['dr']
    rule1_comment = config['rule1']['comment']
    rule2_user = config['rule2']['user']
    rule2_user_other = config['rule2']['user_other']
    rule2_start = config['rule2']['start']
    rule2_hours = config['rule2']['hours']
    rule2_promotion = config['rule2']['promotion']
    rule2_ur = config['rule2']['ur']
    rule2_dr = config['rule2']['dr']
    rule2_comment = config['rule2']['comment']
    http_proxy_state = config['http_proxy']['enabled']
    http_proxy_http = config['http_proxy']['http']
    http_proxy_https = config['http_proxy']['https']

    # 返回值
    return (
        uid, cookie, uploadTimeInterval, sleeptime, interval, rule1_user, rule1_user_other, rule1_start,
        rule1_hours, rule1_promotion, rule1_ur, rule1_dr, rule1_comment, rule2_user, rule2_user_other, rule2_start,
        rule2_hours, rule2_promotion, rule2_ur, rule2_dr, rule2_comment, http_proxy_state, http_proxy_http,
        http_proxy_https
    )
