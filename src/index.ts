import App from "./App";
import ProcessController from "./controllers/ProcessController";
import Cron from "./cron/Cron";
import JobCheckerProcess from "./cron/processes/CheckRuns";
import 'dotenv/config';
import sendSYSStatus from './utils/healthcheck'

const main = async () => {
  const cron = new Cron();
  const processController = new ProcessController();
  const jobCheckerProcess = new JobCheckerProcess();
  sendSYSStatus();
  const controllers = [processController];

  cron.addProcess(jobCheckerProcess);
  const port = 5556;
  const app = new App(controllers, port);
  app.listen();
  return app;
};
main();
export default main;
