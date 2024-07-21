import basic

while True:
    temp = input('basic > ')
    if temp == 'exit':
        break
    tokens, error = basic.run(temp, '<stdin>')
    if error:
        print(error.tostring())
    else:
        print(f'reilang🤖 > {tokens}')