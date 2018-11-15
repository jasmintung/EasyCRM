#_*_coding:utf-8_*_
from easycrmadmin import customer_perm_logic

#权限样式 app_权限名字
perm_dic={
    'crm_table_index':['table_index','GET',[],{},],
    'crm_customers':['customers','GET',[],{},],
    'crm_table_list':['table_list','GET',[],{}],
    'crm_table_list_action':['table_list','POST',[],{}],
    'crm_table_list_view':['table_change','GET',[],{}],
    'crm_table_list_change':['table_change','POST',[],{}],
    'crm_can_access_my_clients':['table_list','GET',[],
                                 {'perm_check':33,'arg2':'test'},
                                 customer_perm_logic.only_view_own_customers],
}
