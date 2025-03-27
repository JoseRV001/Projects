#python chat bot

bot_name: str = 'Bolby'

print(f'Hello! My name is {bot_name}! I am a semi-intelligent chatbot. How can I help you today?')

while True:

    user_input: str = input('You: ').lower()

    if user_input in ['hi','hello','greetings','salutations','what\'s up']:

        print(f'{bot_name}: Greetings! How can I help you today?')

    elif user_input in ['bye','goodbye','good-bye','see ya','see you','later','peace']:

        print(f'{bot_name}: Till next time user! Goodbye!')

        break

    elif user_input in ['what can you do?','what can you help with?']:

        print(f'{bot_name}: I can only do so much being semi intelligent. However I can help with: Basic math operations(add, subtract, multiply, & divide)')

    elif user_input in ['+','add','addition']:

        print(f'Easy! Let\'s do some addition! Please enter any two numbers')
        
        try:

            num1: float = float(input('First number: '))

            num2: float = float(input('Second number: '))

            print(f'{bot_name}: The sum of the two numbers is: {num1} + {num2} = {num1+num2}')

        except ValueError:

                print(f'{bot_name}: Apprently you entered something in that isn\'t a number. Try again!')

    elif user_input in ['-','subtract','subtraction']:

        print(f'Easy! Let\'s do some subtraction! Please enter any two numbers')

        try:

            num1: float = float(input('First number: '))

            num2: float = float(input('Second number: '))

            print(f'{bot_name}: The result of the two numbers is: {num1} - {num2} = {num1-num2}')

        except ValueError:

                print(f'{bot_name}: Apprently you entered something in that isn\'t a number. Try again!')

    elif user_input in ['*','multiply','multiplication']:

        print(f'Easy! Let\'s do some multiplication! Please enter any two numbers')

        try:

            num1: float = float(input('First number: '))

            num2: float = float(input('Second number: '))

            print(f'{bot_name}: The result of the two numbers is: {num1} * {num2} = {num1*num2} ')

        except ValueError:

                print(f'{bot_name}: Apprently you entered something in that isn\'t a number. Try again!')
                
    elif user_input in ['/','divide','division']:

        print(f'Easy! Let\'s do some division! Please enter any two numbers')

        try:

            num1: float = float(input('First number: '))

            num2: float = float(input('Second number: '))

            print(f'{bot_name}: The result of the two numbers is: {num1} / {num2} = {num1/num2}')

        except ValueError:

                print(f'{bot_name}: Apprently you entered something in that isn\'t a number. Try again!')

    else:

        print(f'{bot_name}: I\'m not sure if I can help with that, as I am only semi-intelligent. Please let me help you with the lowly tasks I have been designed for' )