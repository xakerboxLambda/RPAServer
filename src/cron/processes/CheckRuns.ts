import { OkResponse, Process } from "@/interfaces/process";
import axios from "axios";
import { PythonShell } from 'python-shell';
import fs from 'fs';

class JobCheckerProcess implements Process {
  public readonly interval = '*/10 * * * * *'; // Every ten seconds

  private ERRORS_SEND_URL = process.env.ERRORS_SEND_URL;
  private URL_FOR_UPLOAD_TEST = process.env.URL_FOR_UPLOAD_TEST;

  public constructor() {}
  
  public soberiGamno = () => {
    console.log('Hi!');
  }  

  public checkForRuns = async () => {
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
          const runId = job.runId;
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
}
}

export default JobCheckerProcess;

