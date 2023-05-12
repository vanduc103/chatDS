import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ActivatedRoute, Params } from '@angular/router'
import { Services } from '../app.services'
import { Global } from '../global'

@Component({
  selector: 'app-ds',
  templateUrl: './ds.component.html',
  styleUrls: ['./ds.component.scss']
})
export class DsComponent implements OnInit {
  
  urlSafe: SafeResourceUrl;
  url: string = "http://147.47.236.89:38888/tree"
  constructor(private _service: Services, public config: Global, public sanitizer: DomSanitizer, private route: ActivatedRoute) {
    this.config.fullFrame = true
    let self = this
    this.route.params.subscribe((params: Params) => {
        self.urlSafe= self.sanitizer.bypassSecurityTrustResourceUrl(params["url"])
    })
  }
    
  ngOnInit(): void {
    let self = this
  }
  
}
