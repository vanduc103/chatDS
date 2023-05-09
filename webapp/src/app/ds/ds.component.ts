import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-ds',
  templateUrl: './ds.component.html',
  styleUrls: ['./ds.component.scss']
})
export class DsComponent implements OnInit {

  constructor() { }
  prompt: String = ""
  ngOnInit(): void {

  }

  promptTyping(e: any) {
    this.prompt = e.target.textContent;
  }

  
}
