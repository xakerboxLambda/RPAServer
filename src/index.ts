import App from "./App";
import ProcessController from "./controllers/ProcessController";
import Cron from "./cron/Cron";
import JobCheckerProcess from "./cron/processes/CheckRuns";
import 'dotenv/config';

const main = async () => {
  const cron = new Cron();
  const processController = new ProcessController();
  const jobCheckerProcess = new JobCheckerProcess();

  const controllers = [processController];

  cron.addProcess(jobCheckerProcess);
  const port = 5555;
  const app = new App(controllers, port);
  app.listen();
  return app;
};
main();
export default main;
