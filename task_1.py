
start = 100
end = 1000
for number in range(start, end) :
    hundreds = number // 100 
    tens = (number - hundreds * 100) // 10  
    ones = (number - hundreds * 100 - tens * 10)
    if ( hundreds**3 + tens**3 + ones**3 == number ) :
        print(number)