import email_to

def send(address,type):
    server = email_to.EmailServer('smtp.gmail.com', 587, 'ctrl.intelligence@gmail.com', 'Ctrl+Intelligence312##')

    if type == 1:
        server.quick_email(address,"Successful Registration",['Welcome ' + address +'.\n', 'You have successfully been registered on the ObjectID system you will now be able ' +
                                                                    'to log in and use the functionalities of the system.\n', 'Thank you for using ObjectID.'])

send("haainks@gmail.com",1)