
import util from 'util';
const exec = util.promisify(require('child_process').exec);
import axios from 'axios';

interface totalStatus {
    mem: string,
    cpu: string,
    timeStamp: number,
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
    const timeStamp = Date.now()
    return { cpu, mem, timeStamp }
}

const sendSYSStatus = () => setInterval(async () => {
    const serverStatus = await getLoads();
        try {
            axios.post('https://api-dev.gdeeto.com/jobs/health-check', serverStatus);
            //axios.post('https://5218-159-224-233-85.ngrok.io/jobs/health-check', res)
            console.log(serverStatus);
        } catch (e) {
            console.error(e)
        }
    }, 3000)

export default sendSYSStatus;
