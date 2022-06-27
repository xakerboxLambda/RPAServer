import App from "./App";
import ProcessController from "./controllers/ProcessController";
import Cron from "./cron/Cron";
import JobCheckerProcess from "./cron/processes/CheckRuns";
import 'dotenv/config';
import sendSYSStatus from './utils/healthcheck'
import { CleanPlugin } from "webpack";

const main = async () => {
  const cron = new Cron();
  const processController = new ProcessController();
  const jobCheckerProcess = new JobCheckerProcess();
  try {
    sendSYSStatus();
  } catch (e) {
    console.log(e);
  }
  const controllers = [processController];

  cron.addProcess(jobCheckerProcess);
  const port = 5557;
  const app = new App(controllers, port);
  app.listen();
  return app;
};
main();
export default main;
