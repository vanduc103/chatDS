import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HttpClient } from '@angular/common/http'

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { Global } from './global';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { FileSaverModule } from 'ngx-filesaver';
import { DsComponent } from './ds/ds.component';
import { StartComponent } from './start/start.component';

@NgModule({
  declarations: [
    AppComponent,
    DsComponent,
    DsComponent,
    StartComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    BrowserAnimationsModule,
    FileSaverModule,
  ],
  providers: [Global],
  bootstrap: [AppComponent]
})
export class AppModule { }
