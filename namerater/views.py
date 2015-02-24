# coding=utf-8
from common import *

def ban(request, key):
    # Confirm the submission key exists
    submission = Submission.objects.filter(key=key)
    if len(submission):
        submission = submission[0]
        if request.session.get("admin"):
            ban = Ban()
            if submission.meta.user_id:
                ban.user_id = submission.meta.user_id
            ban.ip = submission.meta.ip
            ban.reason = request.GET.get("reason")
            ban.details = request.GET.get("details")
            ban.ends = request.GET.get("ends")
            try:
                ban.save()
                return HttpResponse('{"result":"SUCCESS"}')
            except:
                return HttpResponse('{"result":"FAILURE"}')
    return HttpResponse('{"result":"FAILURE"}')
    
def comment_submit(request):
    key = request.POST.get("key")
    text = request.POST.get("comment")
    
    # Confirm the submission key exists
    submission = Submission.objects.filter(key=key)
    if len(submission):
        submission = submission[0]
    else:
        return redirect("/error/404")
    
    if len(text) == 0:
        return redirect("/view/"+key)
        
    # Check for a ban
    if request.session.get("logged_in"):
        banned = Ban.objects.filter(Q(ip=request.META.get("REMOTE_ADDR")) | Q(user_id=request.session.get("user_id", 0))).count()
    else:
        return redirect("/view/"+key)
        
    if banned:
        return redirect("/error/banned")
    
    # Add comment
    try:
        comment = Comment(key=key, comment=text, user_id=request.session.get("user_id"), ip=request.META.get("REMOTE_ADDR"))
        comment.save()
        
        # Update metadata
        submission.meta.comments += 1
        submission.meta.save()
        
    except:
        return redirect("/view/"+key)
        
    return redirect("/view/"+key)

def delete(request, key):
    # Confirm the submission key exists
    submission = Submission.objects.filter(key=key)
    if len(submission):
        submission = submission[0]
        if request.session.get("admin") or submission.meta.user_id == request.session.get("user_id"):
            Submission.objects.filter(key=key).delete()
            Comment.objects.filter(key=key).delete()
            return HttpResponse('{"result":"SUCCESS"}')
    return HttpResponse('{"result":"FAILURE"}')

def details(request):
    tileset = request.GET.get("tileset", "")
    species = request.GET.get("species", "0")
    output = []
    
    details = Detail.objects.filter(Q(species=species) | Q(species__startswith=species+"-"), directory=tileset).order_by("species")
    for detail in details:
        if detail.species.find("-") != -1:
            form = detail.species.split("-")[1]
            title = form.title()
        else:
            # Remove unset forms for things that always have some form (ex Unown-A)
            if int(species) in ALWAYS_FORM:
                continue
            form = ""
            title = "Standard"
        output.append({"form":form, "form_title":title, "has_back":int(detail.has_back), "has_shiny":int(detail.has_shiny), "has_female":int(detail.has_female)})
        
    if len(output) == 0:
        output.append({"form":"", "form_title":"Standard", "has_back":0, "has_shiny":0, "has_female":0})
    return HttpResponse(json.dumps(output))
    
def error(request, error="general"):
    data = {"title":"Error"}
    if error == "general":
        data["error"] = "An error has occurred. Please try again. If the problem persists, please <a href='mailto:doctordos@gmail.com'>let me know</a> about the issue!"
        data["img"] = "general.png"
    elif error == "404":
        data["error"] = "File not found"
        data["img"] = "404.png"
    elif error == "403":
        data["error"] = "Access denied"
        data["img"] = "403.jpg"
    elif error == "500":
        data["error"] = "Invalid server configuration"
        data["img"] = "500.jpg"
    elif error == "banned":
        data["error"] = "You have been banned!"
        data["img"] = "banned.jpg"
        banned = Ban.objects.filter(Q(ip=request.META.get("REMOTE_ADDR")) | Q(user_id=request.session.get("user_id", 0))).order_by("-id")
        if banned:
            data["error"] += "<br>Your ban will expire on " + str(banned[0].ends) + "<br>You've been banned because...<br>\"" + str(banned[0].reason)+"\""
    elif error == "submission_limit":
        if not request.session.get("logged_in"):
            data["error"] = "You have reached the daily anonymous submission limit. If you want to submit more names, you should log in!"
        else:
            data["error"] = "You have reached your current submission limit for the day. Come back again tomorrow!"
        data["img"] = "submission_limit.jpg"
    elif error == "profile":
        data["error"] = "Profile not found!"
        data["img"] = "profile_missing.jpg"
    elif error == "slurs":
        data["error"] = "A slur was detected in one of your names! Please brush up on the <a href='/help'>rules</a> and try a different name next time."
        data["img"] = "bad_word.jpg"
    elif error == "duplicate":
        data["error"] = "You've submitted a name and Pokémon combination that already exists!"
        data["img"] = "duplicate.png"
    elif error == "submission":
        data["error"] = "Your submission was invalid. Please try again."
        data["img"] = "general.png"
    return render_to_response("error.html", data, context_instance=RequestContext(request))
    
def help(request):
    data = {"title":"Help"}
    return render_to_response("help.html", data, context_instance=RequestContext(request))
    
def index(request, page=1, method="browse", options=None):
    page = int(page)
    data = {"title":method.title() + " - Page " + str(page), "method":method, "votable":True, "page":page, "next":page+1, "prev":max(1, page-1), "options":options}
    data["submissions"] = None
    
    if request.GET.get("sort"): # Searching
        sort = {"date":"-id", "captures":"-meta__score", "name":"name", "species":"species"}.get(request.GET["sort"], "-id")
        data["method"] = "search"
        data["title"] = "Search - Page " + str(page)
        data["qs"] = "?"+request.META.get("QUERY_STRING")
        data["submissions"] = Submission.objects.filter(set_head=False)
        if request.GET.get("species"):
            data["submissions"] = data["submissions"].filter(species=request.GET["species"])
        if request.GET.get("name"):
            data["submissions"] = data["submissions"].filter(name__icontains=request.GET["name"])
        if request.GET.get("keyword"):
            data["submissions"] = data["submissions"].filter(keywords__icontains=request.GET["keyword"])
        if request.GET.get("start"):
            data["submissions"] = data["submissions"].filter(meta__timestamp__gte=request.GET["start"] + " 00:00:00")
        if request.GET.get("end"):
            data["submissions"] = data["submissions"].filter(meta__timestamp__lte=request.GET["end"] + " 23:59:59")
        if request.GET.get("rating"):
            data["submissions"] = data["submissions"].filter(meta__score__gte=request.GET["rating"])
            
        data["submissions"] = data["submissions"].order_by(sort)[(PAGE_SIZE*(page-1)):(PAGE_SIZE*(page-1))+PAGE_SIZE]
    elif method == "browse":
        data["submissions"] = Submission.objects.filter(Q(set="0") | Q(set_head=True)).order_by("-id")[(PAGE_SIZE*(page-1)):(PAGE_SIZE*(page-1))+PAGE_SIZE]
        data["page_link"] = ""
    elif method == "random":
        data["submissions"] = Submission.objects.filter(Q(set="0") | Q(set_head=True)).order_by("?")[:PAGE_SIZE]
        data["page_link"] = "/random"
    elif method == "top" and options == "recent":
        now = datetime.now()
        timediff = now - timedelta(days=30)
        data["submissions"] = Submission.objects.filter(Q(set="0") | Q(set_head=True), meta__timestamp__gte=timediff).order_by("-meta__score", "-id")[(PAGE_SIZE*(page-1)):(PAGE_SIZE*(page-1))+PAGE_SIZE]
        data["page_link"] = "/top/recent"
    elif method == "top" and options == "all":
        data["submissions"] = Submission.objects.filter(Q(set="0") | Q(set_head=True)).order_by("-meta__score", "-id")[(PAGE_SIZE*(page-1)):(PAGE_SIZE*(page-1))+PAGE_SIZE]
        data["page_link"] = "/top/all"
    elif method == "user":
        data["submissions"] = Submission.objects.filter(Q(set="0") | Q(set_head=True), meta__user__key=request.GET.get("key")).order_by("-id")[(PAGE_SIZE*(page-1)):(PAGE_SIZE*(page-1))+PAGE_SIZE]
        data["page_link"] = "/user"
        data["qs"] = "?"+request.META.get("QUERY_STRING")
    
    # Pad to PAGE_SIZE submissions
    if data["submissions"]:
        data["submissions"] = list(data["submissions"])
        while len(data["submissions"]) < PAGE_SIZE:
            data["submissions"].append(Submission())
    
    data["method"] = method
    return render_to_response("index.html", data, context_instance=RequestContext(request))
   
def login(request):
    data = {"title":"Login", "errors":[]}
    if request.POST.get("action", "").lower() == "login":
        user_check = User.objects.filter(name=request.POST.get("username"))
        if not user_check.count():
            data["errors"].append("Username not found!")
            return redirect("/")
            
        user = user_check[0]
        # Verify password
        valid = check_password(request.POST.get("password"), user.password)
        if valid:
            update_session(request, user)
            return redirect("/")
        else:
            data["errors"].append("Invalid password!")
            return redirect("/")
        
    elif request.POST.get("action", "").lower() == "sign up":
        success = True
        # Validate Captcha
        random.seed(request.POST.get("captcha_time"))
        answer = CAPTCHA[random.choice(CAPTCHA.keys())]
        if request.POST.get("captcha").lower() != answer:
            data["errors"].append("You failed to identify the Pokémon!")
            
        # Check for existing username
        if User.objects.filter(name=request.POST.get("username")).count():
            data["errors"].append("Username already exists!")
            
        if User.objects.filter(email=request.POST.get("email")).count():
            data["errors"].append("E-mail address in use!")
            
        if data["errors"]:
            return HttpResponse(str(data["errors"]))
            
        user = User(key=generate_identifier("user"), name=request.POST.get("username"), email=request.POST.get("email"), password=make_password(request.POST.get("password")), active=1)
        try:
            user.full_clean()
            user.save()
            update_session(request, user)
            return redirect("/")
        except ValidationError as e:
            print e
    
    data["captcha_time"] = str(datetime.now())
    random.seed(data["captcha_time"])
    data["captcha_num"] = random.choice(CAPTCHA.keys())
    
    return render_to_response("login.html", data, context_instance=RequestContext(request))
    
def logout(request):
    request.session["logged_in"] = False
    request.session["user_id"] = None
    request.session["userkey"] = None
    request.session["username"] = None
    request.session["icon"] = 0
    request.session["active"] = 0
    request.session["admin"] = 0
    request.session["submissions"] = 0
    request.session["submission_limit"] = 0
    request.session.flush()
    return redirect("/")
    
def name(request):
    data = {"title":"Submit Name"}
    today = date.fromtimestamp(time.time())
    
    # Check for a ban
    if request.session.get("logged_in"):
        banned = Ban.objects.filter(Q(ip=request.META.get("REMOTE_ADDR")) | Q(user_id=request.session.get("user_id", 0))).count()
    else:
        banned = Ban.objects.filter(ip=request.META.get("REMOTE_ADDR")).count()
        
    if banned:
        return redirect("/error/banned")
        
    # Check submission limit
    if request.session.get("logged_in"):
        if request.session["submissions"] == request.session["submission_limit"] and not request.session["admin"]:
            return redirect("/error/submission_limit")
    else:
        if Meta.objects.filter(ip=request.META.get("REMOTE_ADDR"), user_id=None, timestamp__gte=today).count() + 1 >= ANON_LIMIT:
            return redirect("/error/submission_limit")
    
    data["pokemon"] = ALL
    data["sprites"] = Sprite.objects.filter(active=1).order_by("-id")
    return render_to_response("name.html", data, context_instance=RequestContext(request))
    
def name_submit(request):
    today = date.fromtimestamp(time.time())
    # Check for a ban
    if request.session.get("logged_in"):
        banned = Ban.objects.filter(Q(ip=request.META.get("REMOTE_ADDR")) | Q(user_id=request.session.get("user_id", 0))).count()
    else:
        banned = Ban.objects.filter(ip=request.META.get("REMOTE_ADDR")).count()
        
    if banned:
        return redirect("/error/banned")
        
    # Check submission limit
    if request.session.get("logged_in"):
        if request.session["submissions"] == request.session["submission_limit"] and not request.session["admin"]:
            return redirect("/error/submission_limit")
    else:
        if Meta.objects.filter(ip=request.META.get("REMOTE_ADDR"), user_id=None, timestamp__gte=today).count() + 1 >= ANON_LIMIT:
            return redirect("/error/submission_limit")
    
    if (request.POST.get("data")):
        data = json.loads(request.POST["data"], "utf-8")
        
        # Prepare the metadata
        meta = Meta(ip=request.META.get("REMOTE_ADDR"))
        if request.session.get("logged_in"):
            meta.user_id = request.session["user_id"]
        
        # Process keywords
        keywords = ""
        for keyword in data["keywords"]:
            keyword = keyword.strip()
            keywords += keyword + ","
            if len(keywords) > 201:
                break
        keywords = keywords[:-1]
        
        # Create identifier
        identifier = generate_identifier()
        
        # Validate everything.
        submissions = []
        errors = []
        team_member = 0
        for entry in data["submissions"]:
            if team_member >= 6:
                break
            submission = Submission()
            #try:
            submission.name     = entry["name"][:12].strip()
            submission.species  = int(entry["species"])
            submission.back     = bool(entry["back"])
            submission.shiny    = bool(entry["shiny"])
            submission.female   = bool(entry["female"])
            submission.form     = entry["form"]
            submission.sprite   = entry["sprite"]
            """except:
                errors.append("Submission was invalid for Pokémon #"+str(team_member)+"\n")
                print submission.name
                print submission.species
                print submission.back
                print submission.shiny
                print submission.female
                print submission.mega
                print submission.form
                print submission.sprite"""
            
            if not submission.name:
                errors.append("An invalid name was given for Pokémon #"+str(team_member))
            if submission.species < 1 or submission.species > MAX_SPECIES:
                errors.append("An invalid Pokémon was given for Pokémon #"+str(team_member))
            
            # Slur check
            words = submission.name.split(" ")
            for slur in SLURS:
                if slur.lower() in words:
                    return redirect("/error/slurs")
            
            # Validate proper back/shiny/female/mega/form based on sprite set
            if submission.form:
                species_form = str(submission.species) + ("-"+submission.form)
            else:
                species_form = str(submission.species)
            details = Detail.objects.filter(directory=submission.sprite, species=species_form)
            if len(details) == 1:
                details = details[0]
            else:
                return redirect("/error/submission")
                
            if (submission.back and not details.has_back) or (submission.shiny and not details.has_shiny) or (submission.female and not details.has_female):
                return redirect("/error/submission")
            
            submissions.append(submission)
            team_member += 1
        
        ############################################################ Process Set
        
        # Create set identifier (timestamp + ip OR "0")
        if len(data["submissions"]) > 1:
            set = request.META.get("REMOTE_ADDR") + str(int(time.time()))
        else:
            set = "0"
        
        # Create set head
        if len(data["submissions"]) > 1:
            set_head = Submission()
            set_head.set_head = True
            set_head.name = data["set_name"]
            if set_head.name == "":
                set_head.name = "Team"
            set_head.species = -1
            set_head.sprite = "set"
            submissions.append(set_head)
        
        ############################################################ End Set Processing
        
        # Check for duplicates (for non-sets)
        if len(submissions) == 1:
            dupe = Submission.objects.filter(name=submissions[0].name, species=submissions[0].species).count()
            if dupe:
                return redirect("/error/duplicate")
        
        # Quit if there are errors
        if errors:
            return HttpResponse(str(errors))
        
        # Save the metadata
        meta.save()
        
        # Process Shared Data
        for submission in submissions:
            submission.key      = identifier
            submission.set      = set
            submission.keywords = keywords
            submission.meta     = meta
        
        # Save the submissions
        Submission.objects.bulk_create(submissions)
        
        # Update submission count
        if request.session.get("logged_in"):
            request.session["submissions"] += 1
            user = User.objects.get(id=request.session["user_id"])
            user.submissions += 1
            user.save()
        
        # Redirect to view page
        return redirect("/view/"+identifier)
        
    # Error
    return HttpResponse(request.POST.keys())

def profile(request, key):
    data = {"yours":False, "votable":True}
    user = User.objects.filter(key=key)
    page = 1 # For submissions
    comment_list = 10 # Comments to show per page
    comment_page = int(request.GET.get("cpage", 1))
    data["next"] = comment_page + 1
    data["prev"] = max(1, comment_page - 1)
    if len(user) != 1:
        return redirect("/error/profile")
    else:
        user = user[0]
        
    data["title"] = "Profile - " + user.name
    if request.session.get("user_id") == user.id or request.session.get("admin"):
        data["yours"] = True
        data["all"] = ALL
        
        if request.POST.get("icon"):
            user = User.objects.get(id=request.session.get("user_id"))
            user.icon = request.POST.get("icon", 0)
            user.save()
        
    data["user"] = user
    
    # Latest Comments
    comment_keys = {}
    commented_on = Submission.objects.filter(Q(set="0") | Q(set_head=True), meta__user__key=key, meta__comments__gte=1).order_by("-id")
    
    for submission in commented_on:
        if not comment_keys.get(submission.key):
            comment_keys[submission.key] = submission.name
            
    comments = Comment.objects.filter(key__in=comment_keys).order_by("-timestamp")[(comment_list*(comment_page-1)):(comment_list*(comment_page-1))+comment_list]
    parsed_comments = []
    parsed_keys = []
    for comment in comments:
        if comment.key not in parsed_keys:
            comment.name = comment_keys[comment.key]
            parsed_comments.append(comment)
            parsed_keys.append(comment.key)
        
    data["comments"] = parsed_comments
    
    # Submissions - Only the latest six
    data["submissions"] = Submission.objects.filter(Q(set="0") | Q(set_head=True), meta__user__key=key).order_by("-id")[(6*(page-1)):(6*(page-1))+6]
    
    return render_to_response("profile.html", data, context_instance=RequestContext(request))

def report_submit(request):
    key = request.POST.get("key")
    type = request.POST.get("type")
    text = request.POST.get("comment")
    
    # Confirm the submission key exists
    submission = Submission.objects.filter(key=key)
    if len(submission):
        submission = submission[0]
    else:
        return redirect("/error/404")
        
    # Check for a ban
    if request.session.get("logged_in"):
        banned = Ban.objects.filter(Q(ip=request.META.get("REMOTE_ADDR")) | Q(user_id=request.session.get("user_id", 0))).count()
    else:
        return redirect("/view/"+key)
        
    if banned:
        return redirect("/error/banned")
    
    # Add report
    try:
        report = Report(key=key, reason=type, comment=text, user_id=request.session.get("user_id"), ip=request.META.get("REMOTE_ADDR"))
        report.save()
    except:
        return redirect("/view/"+key)
        
    return redirect("/view/"+key)
    
def search(request):
    data = {"title":"Search", "method":"search"}
    data["pokemon"] = ALL
    data["sprites"] = Sprite.objects.all().order_by("-id")
    data["today"] = str(datetime.now())[:10]
    return render_to_response("search.html", data, context_instance=RequestContext(request))
    
def view(request, key):
    data = {"title":"View", "method":"view"}
    submissions = Submission.objects.filter(key=key)
    data["key"] = key
    data["submissions"] = []
    for submission in submissions:
        if submission.set_head:
            data["set_head"] = submission
            continue
            
        submission.tileset = TILESETS.get(submission.sprite, "Unknown")
        
        if submission.meta.user_id == request.session.get("user_id"):
            data["yours"] = True
        data["submissions"].append(submission)
        
    # Get any comments
    if submissions[0].meta.comments:
        data["comments"] = Comment.objects.filter(key=key).order_by("-id")
    return render_to_response("view.html", data, context_instance=RequestContext(request))

def vote(request, key):
    submission = Submission.objects.filter(key=key)
    if len(submission) > 1:
        submission = Submission.objects.filter(key=key, set_head=1)
    submission = submission[0]
        
    count = Vote.objects.filter(submission=submission, ip=request.META.get("REMOTE_ADDR")).count()
    if count:
        return HttpResponse('{"result":"FAILURE", "key":"'+key+'"}')
        
    vote = Vote(submission=submission, vote=1, ip=request.META.get("REMOTE_ADDR")) # Add user
    submission.meta.score += 1
    vote.save()
    submission.meta.save()
    return HttpResponse('{"result":"SUCCESS", "score":'+str(submission.meta.score)+', "key":"'+key+'"}')