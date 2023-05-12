import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router'
import { Services } from '../app.services'
import { Global } from '../global'

@Component({
  selector: 'app-start',
  templateUrl: './start.component.html',
  styleUrls: ['./start.component.scss']
})
export class StartComponent implements OnInit {

  data: any = {
    "email": "",
    "problem_description": "",
    "openai_key": "",
    "file_path": ""
  }

  constructor(public _globalConfig: Global, private _service: Services, private _router: Router, private _route: ActivatedRoute) { }

  ngOnInit(): void {
  }

  onDataSelected(event: any): void {
    let self = this
    let form_data = new FormData()
    let e = event.target.files[0]
    form_data.append('file', e)
    this._service.uploadData(form_data).subscribe((res: any) => {
      if (!("file_path" in res)) alert("Cannot upload file")
      self.data['file_path'] = res["file_path"]
    })
  }
  
  validateData() : boolean {
    if (!this.data.email) return false
    if (!this.data.problem_description) return false
    if (!this.data.file_path) return false
    return true
  }

  start(): void {
    if (!this.validateData()) return
    console.log(123421)
    let data = this.data
    this._service.initData(data).subscribe((res: any) => {
      if (res["url"]) {
        this._router.navigate(['/chat', res["url"]])
      }
    })
  }

}
