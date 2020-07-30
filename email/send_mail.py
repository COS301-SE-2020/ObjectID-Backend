import email_to
server = email_to.EmailServer('smtp.gmail.com', 587, 'ctrl.intelligence@gmail.com', 'Ctrl+Intelligence312##')

server.quick_email('haainks@gmail.com', 'Test',
                    ['# A Heading', 'Something else in the body'],
                   style='h1 {color: blue}')
