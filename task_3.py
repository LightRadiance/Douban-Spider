selected_id = []

## 1-30序号
id = 1
## 1-9循环计数器
counter = 1
while (True) :
    ## 退出循环条件
    if (len(selected_id) == 15) :
        break

    ## 已选中人跳过
    if (id in selected_id) :
        id += 1
        continue
    
    ## 计数器重置
    if (counter > 9) :
        counter = 1
    ## 序号重置
    if (id > 30) :
        id = 1
    
    if (counter ==  9) :
        selected_id.append(id)
    id += 1
    counter += 1
print(selected_id)