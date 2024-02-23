from imports import *

def reset_stgs():
    """used to specify the default settings used for the first connection"""
    colors = [(44, 46, 63),(74, 77, 105),(99, 0, 192),(124, 0, 240),(31, 34, 45),(255,255,255),"dark"]
    #colors = [(230, 230, 230),(210, 210, 210),(169, 77, 255),(206, 153, 255),(31, 34, 45),(20,20,20),"light"] #for lightmode
    file=open('resources/words.txt', 'r')
    autocomplete=file.read().splitlines()
    #print(autocomplete[:10])
    return colors,autocomplete


#FastAPI and sass parameters
app = FastAPI()
sass.compile(dirname=('asset', 'static'))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")










#routes for the all the pages

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, response: Response, fakesession: Union[str, None] = Cookie(default=None)):
    colors,autocomplete=reset_stgs()
    if fakesession != None:logged="Logged in"
    else:logged="Logged off"
    return templates.TemplateResponse(
        request=request, name="index.html", context={"state" : logged, "autocomplete": autocomplete, "colors" : colors, "title" : "Webfloox"}
    )

@app.post("/results", response_class=HTMLResponse)
async def results(request: Request, search: Annotated[str, Form()], fakesession: Union[str, None] = Cookie(default=None)):
    """This is a test function for the navbar search module, it changes the pages title acording to the search input"""
    if fakesession != None:logged="Logged in"
    else:logged="Logged off"
    colors,autocomplete=reset_stgs()
    return templates.TemplateResponse(
        request=request, name="results.html", context={"state" : logged, "autocomplete": autocomplete, "colors" : colors, "title" : "Results for " + search, "search": search}
    )

@app.get("/results")
async def results(response: Response):
    return RedirectResponse(url="/home")

@app.get("/create_cookie") #creates a cookie and redirects to /home
async def create_cookie(response: Response):
    colors,autocomplete=reset_stgs()
    response=RedirectResponse(url="/home")
    response.set_cookie(key="fakesession", value=str(uuid4()), httponly=True)
    return response

@app.get("/logout")
async def logout(response: Response):
    response=RedirectResponse(url="/home")
    response.delete_cookie(key="fakesession", httponly=True)
    return response

@app.get("/", response_class=HTMLResponse) #redirects to /create_cookie
async def index(response: Response):
    return RedirectResponse("/create_cookie")

@app.get("/whoami") #simply a test route to check the fakesession cookie
async def whoami(request: Request, response: Response, fakesession: Union[str, None] = Cookie(default=None)):
    if fakesession != None:logged="Logged in"
    else:logged="Logged off"
    colors,autocomplete=reset_stgs()
    return templates.TemplateResponse(
        request=request, name="whoami.html", context={"fakesession" : fakesession, "state" : logged, "autocomplete": autocomplete, "colors" : colors, "title" : "Webfloox"}
    )


@app.get("/quiz", response_class=HTMLResponse)
async def quiz(request: Request, response: Response, fakesession: Union[str, None] = Cookie(default=None)):
    if fakesession != None:logged="Logged in"
    else:logged="Logged off"
    colors,autocomplete=reset_stgs()
    return templates.TemplateResponse(
        request=request, name="quiz.html", context={"state" : logged, "autocomplete": autocomplete, "colors" : colors, "title" : "Webfloox"}
    )









"""
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)"""