import email_to

def send(address,type):
    server = email_to.EmailServer('smtp.gmail.com', 587, 'ctrl.intelligence@gmail.com', 'Ctrl+Intelligence312##')

    if type == 1:
        server.quick_email(address,"Successful Registration",['Welcome ' + address +'.\n', 'You have successfully been registered on the ObjectID system you will now be able ' +
                                                                    'to log in and use the functionalities of the system.\n', 'Thank you for using ObjectID.'])

    elif type == 2:
        server.quick_email(address, "Account Removed", ['Greetings ' + address + '.\n', 'Your account has been suspended, and you will no longer be able to use the ObjectID system ' +
                                                                'if you require any assistance please mail ctrl.intelligence@gmail.com.\n', 'Thank you for using ObjectID.'])

def flagged_notification(address,lic_plate,flag,image,location, make, model,color):
        server.quick_email(address, "FLAGGED VEHICLE SPOTTED", ["WARNING " + address+ '.\n', "A " + color+" "+ make+" "+model+" with the numberplate "+lic_plate+" has been spotted on a camera at "
        + location + " which is in your area, our system shows that this vehicle is " + flag+"./n", "Please take the nesscary and report the vehicle to the authorities if it is spotted. A snapshot of the vehicle is "+
        "attached to this email."])