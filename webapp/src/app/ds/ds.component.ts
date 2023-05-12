import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { Services } from '../app.services'
import { Global } from '../global'

@Component({
  selector: 'app-ds',
  templateUrl: './ds.component.html',
  styleUrls: ['./ds.component.scss']
})
export class DsComponent implements OnInit {
  
  constructor(private _service: Services, public config: Global, public sanitizer: DomSanitizer) {
    this.config.fullFrame = true
  }
  urlSafe: SafeResourceUrl;
  url: string = "http://147.47.236.89:8888/tree"
  ngOnInit(): void {
    let self = this
    this._service.test().subscribe((res: any) => {
      self.urlSafe= self.sanitizer.bypassSecurityTrustResourceUrl(res['url']);
    })
    

  }
  
}
