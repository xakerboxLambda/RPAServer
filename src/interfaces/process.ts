export interface Process {
    readonly interval: string;
    readonly intervalHealthChecker: string;

    checkForRuns(): void;
    sendSYSStatus(): void;
  }

export interface GetCurrenssyBTC {

}
  
export interface ReceivedData {
    userName: string,
    userPassword: string,
    companyName: string,
    organizationName: string,
    organizationId: number,
    bankQuantity: number,
    runId: string,
    commentPhrase: string,
    errorPhrase: string,
    shortCode: string,
}

export interface OkResponse {
  status: string,
  code: number,
  data: ReceivedData[]
}