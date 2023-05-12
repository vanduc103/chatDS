import {Injectable} from '@angular/core'
import  {HttpClient, HttpHeaders} from '@angular/common/http'

const httpOptions = {
    headers: new HttpHeaders({'Content-Type': 'application/json'})
}

@Injectable({ providedIn: 'root' })
export class Services{
    private url = 'http://147.47.236.89:38500/api/v1'
    private headers: Headers = new Headers({'Content-Type': 'application/json'});
    constructor(private http: HttpClient){

    }

    initData(data: any) {
        return this.http.post(this.url + "/init", data, {"headers": httpOptions.headers})
    }

    uploadData(form: any) {
        return this.http.post(this.url + '/upload_file', form)
    }

    test() {
        return this.http.get(this.url + '/test')
    }
}