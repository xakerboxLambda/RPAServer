import { OkResponse, Process } from "@/interfaces/process";
import axios from "axios";
import util from 'util';
const exec = util.promisify(require('child_process').exec);
import { PythonShell } from 'python-shell';

interface totalStatus {
  mem: string,
  cpu: string,
  timeStamp: number,
}

class JobCheckerProcess implements Process {
  public readonly interval = '*/10 * * * * *'; // Every ten seconds
  public readonly intervalHealthChecker = '*/3 * * * * *';

  private ERRORS_SEND_URL = process.env.ERRORS_SEND_URL;
  private URL_FOR_UPLOAD_TEST = process.env.URL_FOR_UPLOAD_TEST;

  public constructor() {} 

  public checkForRuns = async () => {
    try {
      const runBotProcess = await axios.get<OkResponse>('https://api-dev.gdeeto.com/bots/pending-runs', {
        headers: {
            Authorization: `secret`,
        },
      });

      if (runBotProcess.data.data.length !== 0 ) {
        const recievedJobs = runBotProcess.data.data;

        recievedJobs.forEach(job => {
          console.log(job);
          const stringifiedJob = JSON.stringify(job);

          const options: Object = {
            mode: "text",
            pythonOptions: ["-u"],
            args: stringifiedJob,
          };
  
          PythonShell.run('roboScript.py', options ,(err, pythonLog) =>{
            console.log(pythonLog);
            console.log(err);
          });
        }
      )};
    } catch(e){
        console.log(e);
      }
  }

  private getCPULoad = async () => {
      const { stdout: cpu } = await exec("vmstat 1 2 | tail -1 | awk '{print (100-$15)}'");
      return cpu.replace('\n', '');
  }

  private getMEMLoad = async () => {
      const { stdout: mem } = await exec(`free | grep Mem | awk '{print int($3/$2*100)}'`);
      return mem.replace('\n', '');
  }

  private getLoads = async (): Promise<totalStatus> => {
      const cpu = await this.getCPULoad().then(res => res);
      const mem = await this.getMEMLoad().then(res => res);
      const timeStamp = Date.now()
      return { cpu, mem, timeStamp }
  }

  public sendSYSStatus = async() => {
      const serverStatus = await this.getLoads();
      await axios.post('https://api-dev.gdeeto.com/jobs/health-check', serverStatus);
      //axios.post('https://5218-159-224-233-85.ngrok.io/jobs/health-check', res)
      console.log(serverStatus);
  }
}

export default JobCheckerProcess;

