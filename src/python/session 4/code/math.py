def factorial(n: int):
    '''
    this function returns the factorial of a number n
    
    '''
    if n<0:
        return "factorial is not defined for negative numbers"
    else:
        if n==0 or n==1:
            return 1
        else:
            return n*factorial(n-1)
        
factorial(-1)




print('-------------------------------------------')


def is_prime(n: int): # type hinting
    '''
    Check if a number is prime.
    
    Args:
        n (int): The number to check.
    
    Returns:
        bool: True if the number is prime, False otherwise.
    '''
    if n < 2:
        raise ValueError("Input must be an integer greater than or equal to 2.")
        
    if n > 1:
        for i in range(2, n):
            if n % i == 0:
                return False
        return True
    else:
        return False
    