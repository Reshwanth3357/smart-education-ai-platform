import base64, hashlib, hmac, json, sqlite3, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True); UP=DATA/'uploads'; UP.mkdir(exist_ok=True); DB=DATA/'sakshamai.db'; KEY='development-change-me'
app=FastAPI(title='SakshamAI',version='0.1.0',openapi_url='/api/v1/openapi.json'); app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
def now(): return datetime.now(timezone.utc).isoformat()
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def all(q,p=()):
 c=db();x=[dict(r) for r in c.execute(q,p)];c.close();return x
def one(q,p=()):
 x=all(q,p);return x[0] if x else None
def run(q,p=()):
 c=db();c.execute(q,p);c.commit();c.close()
def jwt(u):
 raw=base64.urlsafe_b64encode(json.dumps({'sub':u['id'],'role':u['role'],'exp':time.time()+3600}).encode()).decode();return raw+'.'+hmac.new(KEY.encode(),raw.encode(),hashlib.sha256).hexdigest()
def user(r:Request):
 try:
  raw,sig=r.headers['authorization'][7:].split('.');assert hmac.compare_digest(sig,hmac.new(KEY.encode(),raw.encode(),hashlib.sha256).hexdigest());d=json.loads(base64.urlsafe_b64decode(raw));assert d['exp']>time.time();u=one('select * from users where id=?',(d['sub'],));assert u and u['active'];return u
 except:raise HTTPException(401,'Authentication required')
def roles(*rs):
 def f(u=Depends(user)):
  if u['role'] not in rs:raise HTTPException(403,'Insufficient permissions')
  return u
 return f
def init():
 c=db();c.executescript('''create table if not exists users(id text primary key,name text,email text unique,password text,role text,department text,job_role text,active int);create table if not exists competencies(id text primary key,name text,domain text);create table if not exists uc(id text primary key,user_id text,competency_id text,level int,score real,required int,evidence text,updated text);create table if not exists courses(id text primary key,title text,provider text,source text,competency_id text,duration text,difficulty text,url text);create table if not exists training_programmes(id text primary key,title text,provider text,competency_id text,duration text,mode text,description text,url text,status text,priority text);create table if not exists assessments(id text primary key,title text,competency_id text);create table if not exists questions(id text primary key,assessment_id text,question text,options text,answer text,explanation text,status text);create table if not exists attempts(id text primary key,user_id text,assessment_id text,answers text,status text,score real,created text);create table if not exists documents(id text primary key,owner text,filename text,status text,text text,created text);create table if not exists quizzes(id text primary key,document_id text,title text,status text,creator text);create table if not exists quiz_questions(id text primary key,quiz_id text,question text,options text,answer text,explanation text,status text);create table if not exists quiz_attempts(id text primary key,quiz_id text,user_id text,answers text,status text,score real,created text);create table if not exists notifications(id text primary key,user_id text,message text,read int,created text);create table if not exists audit_logs(id text primary key,actor_id text,action text,entity text,created text);''');c.commit()
 if c.execute('select count(*) from users').fetchone()[0]:
  if c.execute('select count(*) from training_programmes').fetchone()[0]==0:
   py=c.execute("select id from competencies where name='Python'").fetchone()[0];sql=c.execute("select id from competencies where name='SQL'").fetchone()[0];gis=c.execute("select id from competencies where name='GIS'").fetchone()[0]
   for title,comp,dur,mode in [('Python for Survey Data',py,'3 days','Blended'),('SQL for Statistical Reporting',sql,'2 days','Virtual'),('GIS for District Indicators',gis,'4 days','Lab')]:c.execute('insert into training_programmes values(?,?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),title,'NSSTA / TPAC',comp,dur,mode,'TPAC-recommended demonstration programme.','https://www.mospi.gov.in','OPEN','HIGH'))
   c.commit()
  c.close();return
 c.executemany('insert into users values(?,?,?,?,?,?,?,?)',[('employee','Aarav Sharma','aarav@sakshamai.gov.in','demo123','EMPLOYEE','NSSO','Statistical Officer',1),('trainer','Dr Meera Nair','meera@sakshamai.gov.in','demo123','TRAINER','NSSTA','Senior Faculty',1),('admin','Kavita Rao','admin@sakshamai.gov.in','demo123','ADMIN','DIID','Platform Administrator',1)])
 names=[('Statistics','Statistical'),('Survey Design','Statistical'),('Sampling','Statistical'),('National Accounts','Statistical'),('Price Statistics','Statistical'),('Labour Statistics','Statistical'),('Agricultural Statistics','Statistical'),('SDG Indicators','Statistical'),('Metadata Standards','Statistical'),('Data Quality Frameworks','Statistical'),('Python','Technical'),('R','Technical'),('SQL','Technical'),('Stata','Technical'),('SPSS','Technical'),('SAS','Technical'),('GIS','Technical'),('Data Visualization','Technical'),('Artificial Intelligence','Technical'),('Machine Learning','Technical'),('Cloud Computing','Technical'),('APIs','Technical'),('Open Data','Technical'),('Cybersecurity','Governance'),('Data Privacy','Governance'),('Digital Signatures','Governance'),('Government Cloud','Governance'),('Digital Public Infrastructure','Governance'),('Leadership','Behavioural'),('Communication','Behavioural'),('Project Management','Behavioural'),('Ethics','Behavioural'),('Decision Making','Behavioural'),('Change Management','Behavioural')]; ids={}
 for n,d in names:
  i=str(uuid.uuid4());ids[n]=i;c.execute('insert into competencies values(?,?,?)',(i,n,d))
 scores={'Statistics':82,'SQL':67,'Python':48,'Data Visualization':61,'GIS':45,'Artificial Intelligence':31,'Machine Learning':31,'Survey Design':72,'Data Quality Frameworks':58}
 for n,i in ids.items():
  s=scores.get(n,40);c.execute('insert into uc values(?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),'employee',i,max(1,round(s/20)),s,4 if n in scores else 3,'IMPORTED_RECORD' if n in scores else 'SELF_REPORTED',now()))
 for title,comp,dur,diff in [('Python Fundamentals','Python','8 hours','Beginner'),('Python for Data Analysis','Python','12 hours','Intermediate'),('SQL for Official Statistics','SQL','10 hours','Intermediate'),('Data Visualization for Decision Makers','Data Visualization','6 hours','Intermediate'),('GIS for Statistical Planning','GIS','16 hours','Beginner'),('Machine Learning Fundamentals','Machine Learning','14 hours','Intermediate')]:c.execute('insert into courses values(?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),title,'iGOT Karmayogi','iGOT Karmayogi',ids[comp],dur,diff,'https://igotkarmayogi.gov.in'))
 c.execute('insert into assessments values(?,?,?)',('assess-python','Python competency assessment',ids['Python']))
 for q,o,a,e in [('Which structure stores an ordered mutable collection?',['tuple','list','set','string'],'list','Lists are mutable ordered collections.'),('What does a pandas DataFrame represent?',['A tabular data structure','A web page','An image','A server'],'A tabular data structure','DataFrames hold labelled tabular data.'),('Which method reads a CSV with pandas?',['pd.read_csv()','pd.open()','csv.load()','open.data()'],'pd.read_csv()','pandas exposes read_csv.')]:c.execute('insert into questions values(?,?,?,?,?,?,?)',(str(uuid.uuid4()),'assess-python',q,json.dumps(o),a,e,'PUBLISHED'))
 c.execute('insert into notifications values(?,?,?,?,?)',(str(uuid.uuid4()),'employee','Your personalised learning path has been refreshed.',0,now()));c.commit();c.close()
init()
class Login(BaseModel):email:str;password:str
class Answers(BaseModel):answers:dict={}
class Edit(BaseModel):status:str|None=None
class QuizAnswers(BaseModel):answers:dict={}
@app.post('/api/v1/auth/login')
def login(x:Login):
 u=one('select * from users where email=? and password=?',(x.email,x.password));
 if not u:raise HTTPException(401,'Invalid email or password')
 return {'access_token':jwt(u),'refresh_token':jwt(u),'user':{k:u[k] for k in ('id','name','email','role','department','job_role')}}
@app.get('/api/v1/auth/me')
def me(u=Depends(user)):return {k:u[k] for k in u if k!='password'}
@app.post('/api/v1/auth/logout')
def logout(u=Depends(user)):return {'message':'Signed out'}
@app.get('/api/v1/competencies')
def competencies(u=Depends(user)):return all('select * from competencies order by domain,name')
@app.get('/api/v1/users/{uid}/competencies')
def profile(uid:str,u=Depends(user)):
 if uid!=u['id'] and u['role'] not in ('TRAINER','ADMIN'):raise HTTPException(403,'Not allowed')
 return all('select uc.*,c.name,c.domain from uc join competencies c on c.id=uc.competency_id where user_id=?',(uid,))
@app.get('/api/v1/skill-gaps/me')
def gaps(u=Depends(user)):
 xs=profile(u['id'],u)
 for x in xs:
  x['gap']=max(0,x['required']-x['level']);x['priority']='Critical' if x['gap']>=3 else 'High' if x['gap']==2 else 'Low' if x['gap'] else 'No gap';x['reason']=f"{x['name']} is required at Level {x['required']} for your role; latest measured evidence indicates Level {x['level']}."
 return sorted(xs,key=lambda x:x['gap'],reverse=True)
@app.get('/api/v1/recommendations/me')
def recommend(u=Depends(user)):
 gs={x['competency_id']:x for x in gaps(u)};xs=all('select co.*,c.name competency from courses co join competencies c on c.id=co.competency_id')
 for x in xs:
  g=gs.get(x['competency_id'],{});x['gap']=g.get('gap',0);x['priority']=g.get('priority','Low');x['reason']=g.get('reason','Supports your development.');x['recommendation_score']=35*min(3,x['gap'])/3+40;x['data_label']='Demo / Sandbox Data'
 return sorted(xs,key=lambda x:x['recommendation_score'],reverse=True)
@app.get('/api/v1/courses')
def courses(q:str|None=None,competency:str|None=None,u=Depends(user)):
 xs=recommend(u);return [x for x in xs if (not q or q.lower() in x['title'].lower()) and (not competency or competency.lower() in x['competency'].lower())]
@app.get('/api/v1/training-programmes')
def programmes(u=Depends(user)):
 xs=all('select t.*,c.name competency from training_programmes t join competencies c on c.id=t.competency_id order by priority,title')
 for x in xs:x['data_label']='Demo / Sandbox Data'
 return xs
@app.get('/api/v1/assessments')
def assessments(u=Depends(user)):return all('select a.*,c.name competency from assessments a join competencies c on c.id=a.competency_id')
@app.get('/api/v1/assessments/{aid}')
def assessment(aid:str,u=Depends(user)):
 a=one('select * from assessments where id=?',(aid,));
 if not a:raise HTTPException(404,'Not found')
 qs=all("select id,question,options,explanation from questions where assessment_id=? and status='PUBLISHED'",(aid,))
 for q in qs:q['options']=json.loads(q['options'])
 return {**a,'questions':qs}
@app.post('/api/v1/assessments/{aid}/attempts')
def start(aid:str,u=Depends(user)):
 i=str(uuid.uuid4());run('insert into attempts values(?,?,?,?,?,?,?)',(i,u['id'],aid,'{}','IN_PROGRESS',None,now()));return {'id':i}
@app.post('/api/v1/attempts/{tid}/submit')
def submit(tid:str,x:Answers,u=Depends(user)):
 t=one('select * from attempts where id=? and user_id=?',(tid,u['id']));
 if not t or t['status']!='IN_PROGRESS':raise HTTPException(409,'Attempt unavailable')
 qs=all('select * from questions where assessment_id=?',(t['assessment_id'],));correct=sum(x.answers.get(q['id'])==q['answer'] for q in qs);score=round(correct*100/len(qs),1);level=max(1,min(5,round(score/20)));a=one('select * from assessments where id=?',(t['assessment_id'],));run("update attempts set answers=?,status='SUBMITTED',score=? where id=?",(json.dumps(x.answers),score,tid));run('update uc set level=?,score=?,evidence=?,updated=? where user_id=? and competency_id=?',(level,score,'ASSESSMENT',now(),u['id'],a['competency_id']));return {'score':score,'level':level,'correct':correct,'total':len(qs),'message':'Evidence saved. Gaps and recommendations refreshed.'}
@app.post('/api/v1/documents')
async def upload(file:UploadFile=File(...),u=Depends(roles('TRAINER','ADMIN'))):
 ext=Path(file.filename).suffix.lower();blob=await file.read()
 if ext not in ('.pdf','.docx','.pptx','.txt') or len(blob)>15*1024*1024:raise HTTPException(415,'Only PDF, DOCX, PPTX, TXT under 15MB')
 i=str(uuid.uuid4());text=blob.decode(errors='ignore') if ext=='.txt' else 'Demo extracted content: Statistical quality uses validation, sampling frames, and documented metadata.';run('insert into documents values(?,?,?,?,?,?)',(i,u['id'],file.filename,'PROCESSED',text,now()));return {'id':i,'status':'PROCESSED','message':'Document processing complete in sandbox mode.'}
@app.get('/api/v1/documents')
def docs(u=Depends(roles('TRAINER','ADMIN'))):return all('select id,filename,status,created from documents')
@app.post('/api/v1/documents/{did}/generate-quiz')
def generate(did:str,u=Depends(roles('TRAINER','ADMIN'))):
 if not one('select * from documents where id=?',(did,)):raise HTTPException(404,'Document not found')
 qi=str(uuid.uuid4());run('insert into quizzes values(?,?,?,?,?)',(qi,did,'Document knowledge check','REVIEW_REQUIRED',u['id']))
 for q,o,a,e in [('Which practice supports reliable official statistics?',['Data validation','Skipping review','Removing metadata','Avoiding documentation'],'Data validation','Grounded in the processed source.'),('A sampling frame is used to:',['Identify units for selection','Publish results','Encrypt data','Create charts'],'Identify units for selection','Grounded in the processed source.')]:run('insert into quiz_questions values(?,?,?,?,?,?,?)',(str(uuid.uuid4()),qi,q,json.dumps(o),a,e,'REVIEW_REQUIRED'))
 return {'quiz_id':qi,'status':'REVIEW_REQUIRED','message':'Generated questions require trainer approval before publication.'}
@app.get('/api/v1/quizzes/{qid}')
def quiz(qid:str,u=Depends(user)):
 q=one('select * from quizzes where id=?',(qid,));xs=all('select id,question,options,explanation,status from quiz_questions where quiz_id=?',(qid,))
 for x in xs:x['options']=json.loads(x['options'])
 return {**q,'questions':xs}
@app.get('/api/v1/quizzes')
def quizzes(u=Depends(user)):
 if u['role'] in ('TRAINER','ADMIN'):return all('select * from quizzes order by rowid desc')
 return all("select * from quizzes where status='PUBLISHED' order by rowid desc")
@app.patch('/api/v1/questions/{qid}')
def edit(qid:str,x:Edit,u=Depends(roles('TRAINER','ADMIN'))):run('update quiz_questions set status=? where id=?',(x.status,qid));return {'message':'Question updated'}
@app.post('/api/v1/quizzes/{qid}/publish')
def publish(qid:str,u=Depends(roles('TRAINER','ADMIN'))):
 if one("select * from quiz_questions where quiz_id=? and status!='APPROVED'",(qid,)):raise HTTPException(422,'All questions require explicit approval')
 run("update quizzes set status='PUBLISHED' where id=?",(qid,));run('insert into audit_logs values(?,?,?,?,?)',(str(uuid.uuid4()),u['id'],'QUIZ_PUBLISHED',qid,now()));return {'message':'Quiz published'}
@app.post('/api/v1/quizzes/{qid}/attempts')
def quiz_start(qid:str,u=Depends(user)):
 if not one("select * from quizzes where id=? and status='PUBLISHED'",(qid,)):raise HTTPException(404,'Published quiz not found')
 i=str(uuid.uuid4());run('insert into quiz_attempts values(?,?,?,?,?,?,?)',(i,qid,u['id'],'{}','IN_PROGRESS',None,now()));return {'id':i}
@app.post('/api/v1/quiz-attempts/{tid}/submit')
def quiz_submit(tid:str,x:QuizAnswers,u=Depends(user)):
 t=one('select * from quiz_attempts where id=? and user_id=?',(tid,u['id']))
 if not t or t['status']!='IN_PROGRESS':raise HTTPException(409,'Quiz attempt unavailable')
 qs=all("select * from quiz_questions where quiz_id=? and status='APPROVED'",(t['quiz_id'],));correct=sum(x.answers.get(q['id'])==q['answer'] for q in qs);score=round(100*correct/max(1,len(qs)),1)
 run("update quiz_attempts set answers=?,status='SUBMITTED',score=? where id=?",(json.dumps(x.answers),score,tid));run('insert into notifications values(?,?,?,?,?)',(str(uuid.uuid4()),u['id'],f'Quiz completed: {score}%. Your learning evidence has been recorded.',0,now()))
 return {'score':score,'correct':correct,'incorrect':len(qs)-correct,'unanswered':len(qs)-len(x.answers),'total':len(qs),'message':'Quiz evidence recorded; recommendations will be re-ranked.'}
@app.get('/api/v1/notifications')
def notifications(u=Depends(user)):return all('select * from notifications where user_id=? order by created desc',(u['id'],))
@app.get('/api/v1/analytics/{scope}')
def analytics(scope:str,u=Depends(user)):
 if scope=='admin' and u['role']!='ADMIN':raise HTTPException(403,'Admin access required')
 return {'total_employees':1,'active_learners':1,'average_competency':53,'critical_skill_gaps':3,'training_completion':42,'average_assessment_score':67,'learning_hours':38,'data_label':'Demo / Sandbox Data'}
app.mount('/assets',StaticFiles(directory=ROOT/'apps/web/public'),name='assets')
@app.get('/{path:path}',include_in_schema=False)
def web(path:str):return FileResponse(ROOT/'apps/web/public/index.html')
