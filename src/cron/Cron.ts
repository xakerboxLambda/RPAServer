import cron, { ScheduleOptions } from 'node-cron';
import { Process } from '../interfaces/process';

class Cron {
  private readonly cron: typeof cron;

  private readonly options: ScheduleOptions = {
    scheduled: true,
  };

  public constructor() {
    this.cron = cron;
  }

  public addProcess = (process: Process) => {
    this.cron.schedule(process.interval, process.checkForRuns, this.options).start();

  };
}

export default Cron;
