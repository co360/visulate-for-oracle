/*!
 * Copyright 2019 Visulate LLC. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import { Component } from '@angular/core';
import { RestService } from './services/rest.service';
import { StateService } from './services/state.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  /**
   * Root component for application that displays the data dictionary information
   * from one or more Oracle databases
   * 
   * @param restService - REST API that connects to the database
   * @param state - Object that maintains application state
   */

  constructor(
     private restService: RestService,
     private state: StateService
   ) { }

  ngOnInit(): void {
    // call REST API to get list of databases
     this.restService.getEndpoints()
      .subscribe(endpoints => {
        this.state.saveEndpoints(endpoints)
      });
  }
}
