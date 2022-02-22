
import util from 'util';
const exec = util.promisify(require('child_process').exec);
import axios from 'axios';

interface totalStatus {
    mem: string,
    cpu: string,
    timeStamp?: number,
}

const getCPULoad = async () => {
    const { stdout: cpu } = await exec("vmstat 1 2 | tail -1 | awk '{print (100-$15)}'");
    return cpu.replace('\n', '');
}

const getMEMLoad = async () => {
    const { stdout: mem } = await exec(`free | grep Mem | awk '{print int($3/$2*100)}'`);
    return mem.replace('\n', '');
}

const getLoads = async (): Promise<totalStatus> => {
    const cpu = await getCPULoad().then(res => res);
    const mem = await getMEMLoad().then(res => res);
    return { cpu, mem }
}

const sendSYSStatus = () => setInterval(() => {
    getLoads().then(res => {
        res.timeStamp = Date.now();
        axios.post('https://api-dev.gdeeto.com/jobs/health-check', { data: res })
    })

}, 3000)

export default sendSYSStatus;
