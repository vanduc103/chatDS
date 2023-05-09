import {Injectable} from '@angular/core'
import  {HttpClient, HttpHeaders} from '@angular/common/http'

const httpOptions = {
    headers: new HttpHeaders({'Content-Type': 'application/json'})
}

@Injectable({ providedIn: 'root' })
export class Services{
    private url = 'http://147.47.236.89:39500/api/v1'
    private headers: Headers = new Headers({'Content-Type': 'application/json'});
    constructor(private http: HttpClient){

    }

    initData(data: any) {
        this.http.post(this.url + "/upload", data, {"headers": httpOptions.headers})
    }
    
}