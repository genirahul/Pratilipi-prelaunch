# coding: utf8

#Table stores email of all subscribed visitors. All emails in the table are unique.
db.define_table('subscribers',
                Field('email',requires=(IS_NOT_EMPTY(),IS_EMAIL(error_message='Invalid Email!'),IS_NOT_IN_DB(db,'subscribers.email'))),
                Field('name',requires=(IS_NOT_EMPTY()), default='Test'),
                Field('credit','integer', default=int(500))) #500 initial credit is given to every subscirber.
