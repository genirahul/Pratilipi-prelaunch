# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

#subscription form to be filled by users to subscribe. This function is called from index and subscribe. Actions carried out after form get accepted are different in both cases, hence mentioned in the parent function itself.
def subscribe_form():
    form=FORM(INPUT(_name='email',_placeholder='Enter email id',
                    requires=(IS_NOT_EMPTY(),IS_EMAIL(error_message='Invalid Email!'),)),
              INPUT(_name='name',_placeholder='Enter full name',requires=IS_NOT_EMPTY()),
              INPUT(_type='submit',_value='Subscribe'))
    return form

#mail send to the users as subscription confirmation and invitation.
def email(to,name,mail_type,url):
    from gluon.tools import Mail
    mail = Mail()
    mail.settings.server = 'gae'
    mail.settings.sender = 'no-reply@pratilipi.com'
    mail.settings.login = 'no-reply@pratilipi.com:password'
    if mail_type=='subscription':
        sent= mail.send(to,'www.pratilipi.com',
                        """Hi %s
                             Thank you for subscribing. You are awarded with Rs 500 credit.
                             Share below link with your friends
                             
                             %s

                           Pratilipi Team

                           **THIS IS A SYSTEM GENERATED MAIL. PLEASE DO NOT REPLY
                        """ %(name,url),bcc=['contact@pratilipi.com']
                        )
    elif mail_type=='invitation':
        sent= mail.send(to,'www.pratilipi.com',
                        """Hi,
                             %s invited you to subscribe www.pratilipi.com
                             Click below link to subscribe
                             
                             %s

                           Pratilipi Team

                           **THIS IS A SYSTEM GENERATED MAIL. PLEASE DO NOT REPLY
                        """ % (name,url)
                        )
    return sent

#default function called site is loaded for the first time.
# URL - www.pratilipi.com/pratilipi/default/index
def index():
    response.flash = T("Welcome to Pratilipi!")
    form =subscribe_form()
    if form.accepts(request,session):
        count = db(db.subscribers.email==form.vars.email).count()
        #when user is already subscribed
        if count>0:
            session.flash="You have already subscribed. Invite your friends"
            row =  db(db.subscribers.email==form.vars.email).select(db.subscribers.name)
            redirect(URL('default','invite_friends',args=[form.vars.email,row[0].name]))
        else:
             #Subscription confirmation mail
            mail=email(form.vars.email,form.vars.name,'subscription','')
            #Mail sent successfully
            if mail:
                session.flash="form accepted"
                db.subscribers.insert(email=form.vars.email,name=form.vars.name)
                db.commit()
                redirect(URL('invite_friends', args=[form.vars.email,form.vars.name]))
            #Mail not sent successfully
            elif ~mail:
                response.flash="Unable to send confirmation mail. Please check email address. If problem persists, write us at contact@pratilipi.com"
    elif form.errors:
        response.flash="Error in form"
    return dict(form=form)

#function for inviting friends.
#URL - www.pratilipi.com/pratilipi/default/invite_friends/<inviter's email>/<inviter's name>
def invite_friends():
    url = "http://www.pratilipi.com/%s" %URL('subscribe',args=[request.args(0)])
    form=FORM(INPUT(_name='email',_placeholder='Friend\'s email id',requires=(IS_NOT_EMPTY(),IS_EMAIL(error_message='Invalid Email'))),
              INPUT(_type='submit',_value='Invite Friend'))
    if form.accepts(request,session):
        invitaion=email(form.vars.email,request.args(1),'invitation',url)
        if invitaion:
            response.flash="Invitaion Sent successfully"
        elif ~invitaion:
            response.flash="Unable to send invitaion, please check email id"
    elif form.errors:
        response.flash="Error in form"
    return locals()

#this function is called when user click the subscription unique link.
#URL - www.pratilipi.com/pratilipi/default/subscribe/<inviter's email>
def subscribe():
    response.flash = T("Welcome to Pratilipi!")
    form =subscribe_form()
    if form.accepts(request,session):
        count = db(db.subscribers.email==form.vars.email).count()
        #when user is already subscribed
        if count>0:
            session.flash="You have already subscribed.Invite your friends"
            redirect(URL('default','invite_friends',args=form.vars.email))
        else:
             #Subscription confirmation mail
            mail=email(form.vars.email,form.vars.name,'subscription','')
            #Mail sent successfully
            if mail:
                session.flash="form accepted"
                #adding subscriber to database
                db.subscribers.insert(email=form.vars.email,name=form.vars.name)
                db.commit()
                #Adding credit points to inviter's account.
                invited_by = db(db.subscribers.email==request.args(0)).select().first()
                invited_by.update_record(credit = invited_by.credit+50)
                #next page.
                redirect(URL('invite_friends', args=form.vars.email))
            #Mail not sent successfully
            elif ~mail:
                response.flash="Unable to send confirmation mail. Please check email address. If problem persists, write us at contact@pratilipi.com"
    elif form.errors:
        response.flash="Error in form"
    return dict(form=form)
    return locals()

#Facebook share function
#URL - www.pratilipi.com/default/facebook/<subscriber's email>
def facebook():
    link="http://www.pratilipi.com/%s" %URL('subscribe',args=[request.args(0)])
    url="http://www.facebook.com/sharer.php?u=%s" %link
    redirect(url)
    return locals()

def twitter():
    link="http://www.pratilipi.com/%s" %URL('subscribe',args=[request.args(0)])
    url="http://twitter.com/home?status=%s" %link
    redirect(url)
    return locals()

def google():
    link="http://www.pratilipi.com/%s" %URL('subscribe',args=[request.args(0)])
    url="https://plus.google.com/share?url=%s" %link
    redirect(url)
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
