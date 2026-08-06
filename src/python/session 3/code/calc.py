def add(x: float, y: float) -> float:
    '''  function to add two numbers
    
    Arguments:
        parameter_1 >> The first number
        type_parameter_1 >> x (float)
        
        parameter_2 >> The second number
        type_parameter_2 >> y (float)

        
        returns >> the sum of the two numbers
        type_returns >> float

    '''
    return x + y


def subtract(x: float, y: float) -> float:
    '''  function to subtract two numbers
    
    Arguments:
        parameter_1 >> The first number
        type_parameter_1 >> x (float)
        
        parameter_2 >> The second number
        type_parameter_2 >> y (float)

        
        returns >> the difference of the two numbers
        type_returns >> float

    '''
    return x - y


def multiply(x: float, y: float) -> float:
    '''  function to multiply two numbers
    
    Arguments:
        parameter_1 >> The first number
        type_parameter_1 >> x (float)
        
        parameter_2 >> The second number
        type_parameter_2 >> y (float)

        
        returns >> the product of the two numbers
        type_returns >> float

    '''
    return x * y

def division(x: float, y: float) -> float:
    '''  function to divide two numbers
    
    Arguments:
        parameter_1 >> The first number
        type_parameter_1 >> x (float)
        
        parameter_2 >> The second number
        type_parameter_2 >> y (float)

        
        returns >> the quotient of the two numbers
        type_returns >> float

    '''
    
    return x / y

def main():
    print('Calculator Application')
    print('=====================================')
    print('1 >>> add ')
    print('2 >>> subtract ')
    print('3 >>> multiply ')
    print('4 >>> divide ')
    choice = input('Enter your choice (1/2/3/4): ')
    num1 = float(input('Enter first number: '))
    num2 = float(input('Enter second number: '))
    print(f'you chose {choice} and your numbers are {num1} and {num2}')
    if choice == '1':
        print(f'{num1} + {num2} = the result of addition is {add(num1, num2)}')
    elif choice == '2':
        print(f'{num1} - {num2} = the result of subtraction is {subtract(num1, num2)}')
    elif choice == '3':
        print(f'{num1} * {num2} = the result of multiplication is {multiply(num1, num2)}')
    elif choice == '4':
        print(f'{num1} / {num2} = the result of division is {division(num1, num2)}')
