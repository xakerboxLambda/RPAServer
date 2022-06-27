(()=>{"use strict";var t={187:function(t,e,s){var o=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};Object.defineProperty(e,"__esModule",{value:!0});const r=o(s(582)),i=o(s(860));e.default=class{constructor(t,e){this.listen=()=>{this.app.listen(this.port,(()=>{console.log(`App listening on the port ${this.port}`)}))},this.initializeMiddlewares=()=>{this.app.use(i.default.static("storage")),this.app.use(i.default.json()),this.app.use((0,r.default)({origin:"*",methods:["GET","HEAD","PUT","PATCH","POST","DELETE"],preflightContinue:!1,optionsSuccessStatus:204}))},this.initializeControllers=()=>{this.controllers.forEach((t=>{this.app.use(t.path,t.router)}))},this.app=(0,i.default)(),this.port=e,this.controllers=t,this.initializeMiddlewares(),this.initializeControllers()}}},16:(t,e,s)=>{Object.defineProperty(e,"__esModule",{value:!0});const o=s(860);e.default=class{constructor(t){this.path=t,this.router=(0,o.Router)()}}},618:function(t,e,s){var o=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};Object.defineProperty(e,"__esModule",{value:!0});const r=o(s(16));class i extends r.default{constructor(){super("/runs"),this.initializeRoutes=()=>{},this.initializeRoutes()}}e.default=i},990:function(t,e,s){var o=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};Object.defineProperty(e,"__esModule",{value:!0});const r=o(s(311));e.default=class{constructor(){this.options={scheduled:!0},this.addProcess=t=>{this.cron.schedule(t.interval,t.checkForRuns,this.options).start()},this.cron=r.default}}},24:function(t,e,s){var o=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};Object.defineProperty(e,"__esModule",{value:!0});const r=o(s(167)),i=s(742);e.default=class{constructor(){this.interval="*/10 * * * * *",this.ERRORS_SEND_URL=process.env.ERRORS_SEND_URL,this.URL_FOR_UPLOAD_TEST=process.env.URL_FOR_UPLOAD_TEST,this.checkForRuns=async()=>{const t=await r.default.get("https://api-dev.gdeeto.com/bots/pending-runs",{headers:{Authorization:"secret"}});0!==t.data.data.length&&t.data.data.forEach((t=>{console.log(t);const e={mode:"text",pythonOptions:["-u"],args:JSON.stringify(t)};i.PythonShell.run("roboScript.py",e,((t,e)=>{console.log(e),console.log(t)}))}))}}}},303:function(t,e,s){var o=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};Object.defineProperty(e,"__esModule",{value:!0});const r=o(s(187)),i=o(s(618)),n=o(s(990)),a=o(s(24));s(81);const u=o(s(663)),l=async()=>{const t=new n.default,e=new i.default,s=new a.default;(0,u.default)();const o=[e];t.addProcess(s);const l=new r.default(o,5557);return l.listen(),l};l(),e.default=l},663:function(t,e,s){var o=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};Object.defineProperty(e,"__esModule",{value:!0});const r=o(s(837)).default.promisify(s(493).exec),i=o(s(167));e.default=()=>setInterval((()=>{(async()=>({cpu:await(async()=>{const{stdout:t}=await r("vmstat 1 2 | tail -1 | awk '{print (100-$15)}'");return t.replace("\n","")})().then((t=>t)),mem:await(async()=>{const{stdout:t}=await r("free | grep Mem | awk '{print int($3/$2*100)}'");return t.replace("\n","")})().then((t=>t)),timeStamp:Date.now()}))().then((t=>{try{i.default.post("https://api-dev.gdeeto.com/jobs/health-check",t),console.log(t)}catch(t){console.error(t)}}))}),3e3)},167:t=>{t.exports=require("axios")},582:t=>{t.exports=require("cors")},81:t=>{t.exports=require("dotenv/config")},860:t=>{t.exports=require("express")},311:t=>{t.exports=require("node-cron")},742:t=>{t.exports=require("python-shell")},493:t=>{t.exports=require("child_process")},837:t=>{t.exports=require("util")}},e={};!function s(o){var r=e[o];if(void 0!==r)return r.exports;var i=e[o]={exports:{}};return t[o].call(i.exports,i,i.exports,s),i.exports}(303)})();