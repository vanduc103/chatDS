import {Injectable} from "@angular/core";

@Injectable()
export class Global {
    active_menu: string = ''
    fullFrame: boolean = false
    
    setMenu(menu: string) {
        this.active_menu = menu
    }

}