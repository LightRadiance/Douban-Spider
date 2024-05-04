## 对数组做出一次调整
def array_adjust(array) :
    arr_len = len(array)
    if (arr_len == 0) :
        return  None
    else :
        for i in range(0, arr_len-2) :
            num_3 = array[i:i+3]
            if (num_3[0] <= num_3[2] and
                (num_3[1] > num_3[2] or 
                 num_3[1] < num_3[0])) :
                num_3[1] = (num_3[0] + num_3[2]) // 2
                array[i:i+3] = num_3
                break
    return array

## 检查数组是否非递减
def check_order(array) :
    arr_len = len(array)
    for i in range(0, arr_len-2) :
        if (array[i] > array[i+1]) :
            return False
    return True
            
## 判断数组在小于等于一次调整的情况下是否满足非递减条件
def check_non_decreasing(array) :
    ## 数组为空
    if (len(array) == 0) :
        print("It's a empty array!")
        return
    ## 判断是否有序
    if (check_order(array)) :
        print(array)
        print("Yes!Meet requirements.")
    else :
        ## 进行一次调整
        array = array_adjust(array)

        ## 再次判断是否有序
        if (check_order(array)) :
            print("Yes!Meet requirements")
        else :
            print("Pity!Can't make it non-decreasing.")
            
## 主程序入口      
if __name__ == '__main__' :  
    array = [3, 2, 1, 0] 
    check_non_decreasing(array)