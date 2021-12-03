import { RequestHandler } from "express";
import Controller from "./Controller";
import { PythonShell } from "python-shell";

class ProcessController extends Controller {
  public constructor() {
    super("/runs");

    this.initializeRoutes();
  }

  private initializeRoutes = () => {
    // this.router.post("/start", this.startProcess);
  };

  // private startProcess: RequestHandler = (req, res) => {
  //   const bodyReq = req.body;
  //   const search = bodyReq.search;
  //   const url = bodyReq.url;
  //   console.log(bodyReq);
  //   console.log(search);

  //   let options: Object = {
  //     mode: "text",
  //     pythonOptions: ["-u"],
  //     args: [search, url],
  //   };

  //   PythonShell.run('script.py', options, function (err) {
  //     if (err) throw err;
  //     console.log("Process finished!");
  //   });
  // };

}

export default ProcessController;
