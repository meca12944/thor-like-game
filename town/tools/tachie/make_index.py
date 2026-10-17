# writes town/assets/tachie/index.json (data the engine reads)
import json,os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../assets/tachie')
names={'hero':'필멸자','a_tailor':'리네트','h_mystic':'베일라','g_dancer':'자이라','f_diver':'마렌','e_tailor':'로자린드','c_priest':'이벨린','d_yuna':'유나'}
EX=['neutral','smile','angry','sad','surprised','blush']
out={'version':1,'size':[750,2150],'expressions':EX,'alias':{'normal':'neutral','happy':'smile','mad':'angry','cry':'sad','shock':'surprised','shy':'blush'},'chars':{}}
for cid,n in names.items():
    out['chars'][cid]={'name':n,'side':'left' if cid=='hero' else 'right','scale':1.03 if cid=='hero' else 1.0,
      'expr':{e:f'{cid}_{e}.png' for e in EX if os.path.exists(f'{D}/{cid}_{e}.png')}}
json.dump(out,open(D+'/index.json','w'),ensure_ascii=False,indent=1);print('ok',len(out['chars']))
