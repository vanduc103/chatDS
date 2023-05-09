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

  email: string = ""
  prompt: string = ""
  data: any = ""

  constructor(public _globalConfig: Global, private _service: Services, private _router: Router, private _route: ActivatedRoute) { }

  ngOnInit(): void {
  }

  onDataSelected(e: any): void {
    let self = this
    let reader = new FileReader()
    reader.readAsText(e.target.files[0])
    reader.onload = () => {
      self.data = reader.result
    }
  }

  processData(d: any): string {
    let data = ""
    return data
  }
  start(): void {
    if (!this.data) return
    let data = this.processData(this.data)
    let obj = {
      email: this.email,
      prompt: this.prompt,
      data: data
    }
    this._service.initData(obj)
  }

}
