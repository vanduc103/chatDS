import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DsComponent } from './ds/ds.component';
import { StartComponent } from './start/start.component';

const routes: Routes = [
    {path: '', component: StartComponent, pathMatch: 'full'},
    {path: 'initial', component: StartComponent, pathMatch: 'full'},
    {path: 'chat/:url', component: DsComponent, pathMatch: 'full'},
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
