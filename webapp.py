from imports import *

def reset_stgs(lightmode):
    """used to specify the default settings used for the first connection"""
    if lightmode : colors = [(230, 230, 230),(180, 180, 180),(169, 77, 255),(206, 153, 255),(31, 34, 45),(20,20,20),"light"] #for lightmode
    else : colors = [(44, 46, 63),(74, 77, 105),(99, 0, 192),(124, 0, 240),(31, 34, 45),(255,255,255),"dark"]
    file=open('resources/words.txt', 'r')
    autocomplete=file.read().splitlines()
    return colors,autocomplete


#FastAPI and sass parameters
app = FastAPI()
sass.compile(dirname=('asset', 'static'))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



temp_data={None : {"lightmode" : False}}


def generic_render(request,fakesession,dictionary,name,title):
    """handles the light/dark modes for you, uses a dictionary to pass information to the pages"""
    if fakesession != None:logged="Logged in"
    else:logged="Logged off"
    colors=reset_stgs(temp_data[fakesession]["lightmode"])[0]
    return templates.TemplateResponse(
        request=request, name=name, context={"fakesession" : fakesession ,"state" : logged, "dictionary": dictionary, "colors" : colors, "title" : title}
    )




#special routes

@app.get("/create_cookie") #creates a cookie and redirects to /home
async def create_cookie(response: Response):
    global temp_data
    colors,autocomplete=reset_stgs(False)
    uuid=str(uuid4())
    temp_data[uuid]={}
    temp_data[uuid]["lightmode"]=False
    temp_data[uuid]["search"]=[]
    response=RedirectResponse(url="/home")
    response.set_cookie(key="fakesession", value=uuid, httponly=True)
    return response

@app.get("/logout")
async def logout(response: Response):
    response=RedirectResponse(url="/home")
    response.delete_cookie(key="fakesession", httponly=True)
    return response

@app.get("/") #redirects to /create_cookie
async def index(response: Response):
    return RedirectResponse(url="/create_cookie")










#routes for the all the pages

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, response: Response, fakesession: Union[str, None] = Cookie(default=None)):
    global temp_data
    autocomplete=reset_stgs(False)[1]
    return generic_render(request,fakesession,{"autocomplete":autocomplete},"index.html","Webfloox")

@app.post("/home", response_class=HTMLResponse)
async def home(request: Request, response: Response, switchmode: Annotated[str, Form()], fakesession: Union[str, None] = Cookie(default=None)):
    global temp_data
    if switchmode == "1" and fakesession!=None : temp_data[fakesession]["lightmode"]=1-temp_data[fakesession]["lightmode"]
    autocomplete=reset_stgs(False)[1]
    return generic_render(request,fakesession,{"autocomplete":autocomplete},"index.html","Webfloox")







@app.post("/results", response_class=HTMLResponse)
async def results(request: Request, search: Annotated[str, Form()] = "", switchmode: Annotated[str, Form()] = None, fakesession: Union[str, None] = Cookie(default=None)):
    """This is a test function for the navbar search module, it changes the pages title acording to the search input"""
    global temp_data
    if fakesession!=None :
        if search == "" : search=temp_data[fakesession]["search"][-1]
        else : temp_data[fakesession]["search"].append(search)
    if switchmode == "1" and fakesession!=None : temp_data[fakesession]["lightmode"]=1-temp_data[fakesession]["lightmode"]
    autocomplete=reset_stgs(False)[1]
    return generic_render(request,fakesession,{"autocomplete":autocomplete,"search":search},"results.html","Results for " + search)

@app.get("/results")
async def results(response: Response):
    return RedirectResponse(url="/home")







@app.get("/whoami") #simply a test route to check the fakesession cookie
async def whoami(request: Request, response: Response, fakesession: Union[str, None] = Cookie(default=None), user_agent: Annotated[str | None, Header()] = None):
    global temp_data
    client=str(request.client)
    autocomplete=reset_stgs(False)[1]
    if fakesession!=None :
        search=temp_data[fakesession]["search"]
        return generic_render(request,fakesession,{"autocomplete":autocomplete,"user_agent":user_agent,"client":client, "search":search},"whoami.html","Webfloox - Who am I ?")
    else : return generic_render(request,fakesession,{"autocomplete":autocomplete,"user_agent":user_agent,"client":client},"whoami.html","Webfloox - Who am I ?")


@app.post("/whoami") #simply a test route to check the fakesession cookie
async def whoami(request: Request, response: Response, switchmode: Annotated[str, Form()], fakesession: Union[str, None] = Cookie(default=None), user_agent: Annotated[str | None, Header()] = None):
    global temp_data
    client=str(request.client)
    if switchmode == "1" and fakesession!=None : temp_data[fakesession]["lightmode"]=1-temp_data[fakesession]["lightmode"]
    autocomplete=reset_stgs(False)[1]
    if fakesession!=None :
        search=temp_data[fakesession]["search"]
        return generic_render(request,fakesession,{"autocomplete":autocomplete,"user_agent":user_agent,"client":client, "search":search},"whoami.html","Webfloox - Who am I ?")
    else : return generic_render(request,fakesession,{"autocomplete":autocomplete,"user_agent":user_agent,"client":client},"whoami.html","Webfloox - Who am I ?")









@app.get("/quiz", response_class=HTMLResponse)
async def quiz(request: Request, response: Response, fakesession: Union[str, None] = Cookie(default=None)):
    global temp_data
    autocomplete=reset_stgs(False)[1]
    return generic_render(request,fakesession,{"autocomplete":autocomplete},"quiz.html","Webfloox - Quiz")



@app.post("/quiz", response_class=HTMLResponse)
async def quiz(request: Request, response: Response, switchmode: Annotated[str, Form()], fakesession: Union[str, None] = Cookie(default=None)):
    global temp_data
    if switchmode == "1" and fakesession!=None : temp_data[fakesession]["lightmode"]=1-temp_data[fakesession]["lightmode"]
    autocomplete=reset_stgs(False)[1]
    return generic_render(request,fakesession,{"autocomplete":autocomplete},"quiz.html","Webfloox - Quiz")




"""
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)"""