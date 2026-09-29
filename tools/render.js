const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const {spawn}=require('child_process');
const FF=process.env.FF;
const [,, a, b, out]=process.argv; const A=+a,B=+b, FPS=30, W=1920, H=1080;
(async()=>{
 const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
 const pg=await br.newPage({viewport:{width:W,height:H},deviceScaleFactor:1});
 const errs=[];pg.on('pageerror',e=>errs.push(e.message));
 await pg.goto('file://'+process.cwd()+'/render2.html?render=1');
 await pg.evaluate(()=>document.fonts.ready);
 await pg.waitForTimeout(600);
 const ff=spawn(FF,['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r',String(FPS),out],{stdio:['pipe','inherit','inherit']});
 const el=await pg.$('.frame');
 const t0=Date.now();
 for(let f=A;f<B;f++){
   await pg.evaluate(t=>window.mathFilm.seek(t),f/FPS);
   const buf=await el.screenshot({type:'jpeg',quality:94});
   if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
   if((f-A)%100===0)console.error(out,f-A,'/',B-A,((Date.now()-t0)/1000).toFixed(0)+'s');
 }
 ff.stdin.end();await new Promise(r=>ff.on('close',r));
 console.error(out,'done',errs);await br.close();
})();
