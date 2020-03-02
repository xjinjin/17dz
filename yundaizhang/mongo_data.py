from pymongo import MongoClient

conn = MongoClient('127.0.0.1',27017)

db = conn.yundaizhang


#一个云代账户对应一个集合，一个集合下是多个公司
#创建公司集合, account是账户名 baiyi
def create_dbs(acount):
    new_set = db.acount
    return new_set


#创建账户对应集合目录
def create_set(new_set,company_list):

    for company in company_list:
        new_set.insert(
            {company:
                {
                    '凭证':'none',
                    '科目余额':'none',
                    '辅助核算余额':'none',
                    '基础设置':{
                        '科目':'none',
                        '辅助核算':'none',
                        '币别':'data'
                    }
                }
            }
        )


#更新凭证
def update_voucher(company,data):

    db.baiyi.update(
        {
            '%s.凭证'%company:'none'
        },
        {
            '$set':{
                '%s.凭证'%company:data
            }
        }
    )


# 更新科目余额表
def update_kmsheet(company,data):

    db.baiyi.update(
        {
            '%s.科目余额' % company: 'none'
        },
        {
            '$set': {
                '%s.科目余额' % company: data
            }
        }
    )

# 更新辅助核算余额表
def update_fzsheet(company,data):

    db.baiyi.update(
        {
            '%s.辅助核算余额' % company: 'none'
        },
        {
            '$set': {
                '%s.辅助核算余额' % company: data
            }
        }
    )


# 更新基础设置.科目
def update_setting_km(company,data):

    db.baiyi.update(
        {
            '%s.基础设置.科目' % company: 'none'
        },
        {
            '$set': {
                '%s.基础设置.科目' % company: data
            }
        }
    )


# 更新基础设置.币别
def update_setting_bibie(company,data):

    db.baiyi.update(
        {
            '%s.基础设置.币别' % company: 'none'
        },
        {
            '$set': {
                '%s.基础设置.币别' % company: data
            }
        }
    )


# 更新基础设置.辅助核算
def update_setting_fzhs(company,data):

    db.baiyi.update(
        {
            '%s.基础设置.辅助核算' % company: 'none'
        },
        {
            '$set': {
                '%s.基础设置.辅助核算' % company: data
            }
        }
    )
