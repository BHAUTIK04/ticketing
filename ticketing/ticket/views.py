# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.models import User
import logging
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

logger = logging.getLogger(__name__)

def mongoConn():
    print settings.MONGODB_URL
    print settings.MONGODB_DATABASE
    conn = MongoClient('mongodb://'+settings.MONGODB_URL)
    db = conn[settings.MONGODB_DATABASE]
    return db

def index(request):
    logger.info("Index page.")
    return render(request, "index.html")

@csrf_exempt
def createUser(request):
    """
        URI: hostname:8000/createuser
        Registration for new user
        @param email: Email id /unique email id for registration
        @param password: Password which will be use for registaration
        @param first_name: first nameof user
        @param last_name: last name of user
        This parameter can be use for login later.
    """
    try:
        if request.method == "POST":
            req_data = json.loads(request.body)
            logger.info("Create user request {}".format(req_data))
            _email = req_data.get("email", "").lower()
            _password = req_data.get("password", "")
            if _email and _password:
                avail = User.objects.filter(username=_email).count()
                if avail>0:
                    return HttpResponse(json.dumps({"flag":"error","message":"Email already Exists"}),status=409)
                user=User.objects.create_user(username=_email, password=_password, email=_email)
                user.first_name = req_data.get("first_name", " ")
                user.last_name = req_data.get("last_name", " ")
                if "staff" in req_data and req_data["staff"]:
                    user.is_staff = True
                user.save()
                response_data = {"flag":"success","message":"User Created"}
                return HttpResponse(json.dumps(response_data))
            else:
                response_data = {"flag":"error", "message":"Null value not allowed for email and password"}
                return HttpResponse(json.dumps(response_data))
        else:
            logger.info("Create user GET request")
            response_data = {"flag":"error", "message":"Only POST request allowed"}
            return HttpResponse(json.dumps(response_data), status = 405)
    except Exception as e:
        logger.error("Error while creatting user, reason is {}".format(e))
        return HttpResponse(json.dumps({"flag":"error", "message":"Error."}), status = 500)

@csrf_exempt
def userLogin(request):
    """
        URI: hostname:8000/login
        User login for registered user.
        @param email: email id with user registered.
        @param password: Password given while registration.
    """
    try:
        if request.method=="POST":
            if request.user.is_authenticated():
                response_data = {"message": "User is already authenticate"}
                return HttpResponse(json.dumps(response_data), status = 400)
            else:
                login_data = json.loads(request.body)
                username = login_data.get("email")
                password = login_data.get("password")
                logger.info("user login request for {}".format(username))
                try:
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    logger.info("user {} is loggedin successfully".format(username))
                    response_data = {"flag":"success", "message":"User loggedin successfully"}
                    return HttpResponse(json.dumps(response_data))
                except Exception as e:
                    logger.error("user login request failed due to {} for user {} ".format(e, username))
                    response_data = {"flag":"error", "message":"Entered Username/password is wrong."}
                    return HttpResponse(json.dumps(response_data), status = 400)
        else:
            return HttpResponse(json.dumps({"flag":"error", "message": "Only POST method allowed."}), status = 405)
    except Exception as e:
        logger.error("User login error {}".format(e))
        response_data = {"flag":"error", "msg":"Something went wrong. Please try again"}
        return HttpResponse(json.dumps(response_data), status = 500)

@csrf_exempt
def userLogout(request):
    """
        URI: hostname:8000/logout
        Logout user if user is loggedin. No input data is required.
    """
    try:
        if request.method == "GET":
            if request.user.is_authenticated():
                logger.info("User {} is logout".format(request.user))
                logout(request)
                response_data = {"flag":"success", "message":"User logout"}
                return HttpResponse(json.dumps(response_data))
            else:
                response_data = {"flag":"error", "message":"You are not logged in. Please log in and try again"}
                return HttpResponse(json.dumps(response_data), status = 401)
        else:
            response_data = {"flag":"error", "message":"Only GET method allowed"}
            return HttpResponse(json.dumps(response_data), status = 405)
    except Exception as e:
        logger.error("User logout error {}".format(e))
        response_data = {"flag":"error", "msg":"Something went wrong. Please try again"}
        return HttpResponse(json.dumps(response_data), status = 500)




@csrf_exempt
def ticket(request):
    """
        URI: hostname:8000/ticket
        POST:Raise/Generate ticket for any available product with proper description.
            emp_id and emp_email from request.Ticket_id is ObjectId.
            status can be "pending","open","resolved","closed".
            But Initial status of any request is pending. Later it can be updated by admin.
            Request params:
                @param description:ticket description
                @param product: product type/ product name Eg:- Pay, Reimburse, Machine Required, Attendance
        GET:
            Request to listout all the ticket raised/generated by loggedin user. No params required.
        PUT:
            Request to modify the ticket description.
            @param ticket_id: Ticket id/ObjectId
            @param description: Description to modify
        DELETE:
            Request to delete generated ticket.
            @param ticket_id: Ticket id
        All the above method requires authenticated user. If user is not loggedin request will be fail.
    """
    try:
        if not request.user.is_authenticated():
            return HttpResponse(json.dumps({"message": "You are not logged in. Please log in and try again"}), status=401)
        db = mongoConn()
        emp_id = int(request.user.id)
        emp_email = request.user.email
        if request.method == "POST":
            try:
                request_data = json.loads(request.body)
                ticket_id = ObjectId()
                description = request_data.get("description", " ")
                product_name = request_data.get("product", " ")
                logger.info("Ticker request came from {} for this product {}".format(emp_id, product_name))
                try:
                    #mongodb insertion
                    insert_ticket = db["ticket"].insert({"_id":ticket_id,
                                                         "ticket_id":str(ticket_id),
                                                         "description": description,
                                                         "emp_id": emp_id,
                                                         "emp_email":emp_email,
                                                         "created_at": str(datetime.now()),
                                                         "status": "pending",
                                                         "product": product_name})
                    logger.info("ticker inserted with ticket number {}".format(insert_ticket))
                    response_data = {"flag":"success",
                                     "message": "Ticket Created, Admin will get back to you soon."}
                    return HttpResponse(json.dumps(response_data), status=201)
                except Exception as e:
                    logger.error("Error while insert in mongodb, due to {}".format(e))
                    response_data = {"flag":"error",
                                     "message": "Not able to create ticket now please try again later"}
                    return HttpResponse(json.dumps(response_data), status = 400)
            except Exception as e:
                logger.error("Error while creating ticket, due to {}".format(e))
                response_data ={"flag":"error", "message": "Not able to create ticket now please try again later"}
                return HttpResponse(json.dumps(response_data), status=500)

        elif request.method == "GET":
            try:
                data = db["ticket"].find({"emp_id": emp_id}, {"_id":0})
                tickets = list(data)
                return HttpResponse(json.dumps({"flag":"success", "tickets": tickets}))
            except Exception as e:
                logger.error("Not able to fetch tickets, due to {}".format(e))
                response_data = {"flag":"error", "message": "Not able to fetch tickets."}
                return HttpResponse(json.dumps(response_data), status = 500)

        elif request.method == "PUT":
            try:
                if request.body:
                    request_data = json.loads(request.body)
                    if "description" in request_data and "ticket_id" in request_data:
                        description = request_data.get("description")
                        ticket_id = request_data.get("ticket_id")
                        logger.info("Modify ticket request for ticket {}".format(ticket_id))
                        # mongodb update
                        modified_response = db["ticket"].update({"ticket_id": ticket_id,
                                                                 "emp_id": emp_id},
                                                                {"$set":{"description": description,
                                                                         "modified_at": str(datetime.now())}})
                        logger.info("Response for modified ticket {} is {}".format(ticket_id, modified_response))
                        if modified_response['updatedExisting']:
                            response_data = {"flag":"success", "message": "Modified successfully"}
                            return HttpResponse(json.dumps(response_data))
                        else:
                            response_data = {"flag":"error", "message": "Ticket can not be modified."}
                            return HttpResponse(json.dumps(response_data))
                    else:
                        logger.error("ticket_id and description is not provided in request")
                        response_data = {"flag":"error", "message": "Missing data in request. either description or ticket_id"}
                        return HttpResponse(json.dumps(response_data))
                else:
                    logger.error("Not able to modify ticket, due to data not available in request")
                    response_data = {"flag":"error", "message": "Request body is empty."}
                    return HttpResponse(json.dumps(response_data))
            except Exception as e:
                logger.error("Not able to modify ticket, due to {}".format(e))
                response_data = {"flag":"error", "message": "Can not modify ticket at the moment, Please try again later."}
                return HttpResponse(json.dumps(response_data), status = 500)

        elif request.method == "DELETE":
            try:
                if request.body:
                    request_data = json.loads(request.body)
                    if request_data:
                        emp_id = int(request.user.id)
                        ticket_id = request_data.get("ticket_id", "")
                        if ticket_id:
                            print dir(db["ticket"])
                            a = db["ticket"].find_one_and_delete({"emp_id":emp_id, "ticket_id": ticket_id})
                            if a:
                                db["ticket_deleted"].insert(a)
                                response_data = {"flag":"success", "message": "Ticket {} deleted successfully.".format(ticket_id)}
                                return HttpResponse(json.dumps(response_data))
                            else:
                                response_data = {"flag":"success", "message": "Ticket {} can not delete, Not available in database".format(ticket_id)}
                                return HttpResponse(json.dumps(response_data), status = 204)
                    else:
                        logger.error("delete ticket request does not contain ticket_id")
                        response_data = {"flag":"error", "message": "Please provide ticket id."}
                        return HttpResponse(json.dumps(response_data))
                else:
                    logger.error("Delete request for")
                    response_data = {"flag":"error", "message": "Empty Ticket id can not be deleted"}
                    return HttpResponse(json.dumps(response_data))
            except Exception as e:
                logger.error("Delete request from {} can not serve".format(request.user))
                response_data = {"flag":"error", "message": "Ticket can not be deleted,please try later."}
                return HttpResponse(json.dumps(response_data), status = 500)

    except Exception as e:
        logger.info("Error {}".format(e))
        response_data = {"flag":"error", "message": "Service not available, Contact admin or try again later"}
        return HttpResponse(json.dumps(response_data),status=400)




def searchTicket(request, ticket_id):
    """
        To search ticket by ticket id
        Eg: hostname:8000/searchticket/ticket_id
        ticket_id should not be empty or incorrect.
        ticket_id is 24 char long bson objectid.
    """
    try:
        if not request.user.is_authenticated():
            response_data = {"status": "error", "message": "You are not logged in. Please log in and try again" }
            return HttpResponse(json.dumps(response_data), status = 401)
        db = mongoConn()
        if request.method == "GET":
            if ticket_id and len(ticket_id) == 24:
                logger.info("Request to search for ticket id {}".format(ticket_id))
                ticket_detail = db["ticket"].find_one({"ticket_id":ticket_id}, {"_id":0})
                if ticket_detail:
                    response_data = {"flag":"success", "ticket": ticket_detail}
                    status_code = 200
                else:
                    response_data = {"flag":"error", "ticket": {}}
                    status_code = 404
                return HttpResponse(json.dumps(response_data),status = status_code)
            else:
                logger.debug("Invalid ticket_id")
                response_data = {"flag":"error", "message": "Invalid ticket id, try again with correct id"}
                return HttpResponse(json.dumps(response_data))
        else:
            logger.debug("Request to searchticket other than GET.")
            response_data = {"flag":"error", "message": "Only GET request is allowed for this API"}
            return HttpResponse(json.dumps(response_data),status=405)
    except Exception as e:
        logger.error("Error While searching ticket {}".format(e))
        response_data = {"flag":"error", "message": "Service not available, Contact admin or try again later"}
        return HttpResponse(json.dumps(response_data),status=500)


@csrf_exempt
def adminTicket(request):
    """
        Admin/staff action api.
        admin can change status of ticket and add remarks for action.
        Admin can filter tickes based on status, product, email, empid and lists all.
        PUT: hostname:8000/adminticket
            @param ticket_id: id of ticket which is requested to change
            @param status: new status of tickets
            @param remarks: admin remarks

        GET: hostname:8000/adminticket OR hostname:8000/adminticket?status=pending
            returns all tickets with given arguments
    """
    try:
        if request.user.is_authenticated():
            if request.user.is_staff:
                admin_user_id = request.user.id
                admin_user_email = request.user.email
                db = mongoConn() # status pending, open, close, resolved
                if request.method == "GET":
                    if request.GET:
                        _param = request.GET.dict()
                        _mongo_response = db["ticket"].find(_param,{"_id":0})
                    else:
                        _mongo_response = db["ticket"].find({},{"_id":0})
                    tickets = list(_mongo_response)
                    response_data = {"flag":"success", "tickets": tickets}
                    return HttpResponse(json.dumps(response_data))
                elif request.method == "PUT":
                    request_data = json.loads(request.body)
                    if "status" in request_data and "ticket_id" in request_data:
                        ticket_status = request_data["status"]
                        ticket_id = request_data["ticket_id"]
                        admin_remarks = request_data.get("remarks", "")
                        mongo_response = db["ticket"].update({"ticket_id": ticket_id},
                                                             {"$set":{"status": ticket_status,
                                                                      "admin_remarks": admin_remarks,
                                                                      "admin_action_at": str(datetime.now()),
                                                                      "admin_id": admin_user_id,
                                                                      "admin_email": admin_user_email}})
                        print mongo_response
                        if mongo_response and mongo_response["updatedExisting"]:
                            response_data = {"flag":"success", "message": "Status updated successfully"}
                            return HttpResponse(json.dumps(response_data))
                        else:
                            response_data = {"flag":"success", "message": "Status remains same"}
                            return HttpResponse(json.dumps(response_data))
                    else:
                        response_data = {"flag":"error", "message": "Provide ticket_id and status in request body."}
                        return HttpResponse(json.dumps(response_data))
                else:
                    response_data = {"flag":"success", "message": "Only PUT and GET method is allowed"}
                    return HttpResponse(json.dumps(response_data), status = 405)
            else:
                logger.error("Unauthorised user accessed API.")
                response_data = {"flag":"error", "message": "You are not an authorised user for this api"}
                return HttpResponse(json.dumps(response_data))
        else:
            logger.error("Unauthenticate user access")
            response_data = {"flag":"error", "message": "You are not logged in. Please log in and try again."}
            return HttpResponse(json.dumps(response_data), status = 401)
    except Exception as e:
        logger.error("Error in admin API {} ".format(e))
        response_data = {"flag":"error", "message": "Error while serving this api"}
        return HttpResponse(json.dumps(response_data))
