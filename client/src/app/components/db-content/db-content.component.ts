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

import { Component, OnInit } from '@angular/core';
import { RestService } from '../../services/rest.service';
import { StateService } from '../../services/state.service';
import { EndpointModel, EndpointListModel } from '../../models/endpoint.model';
import { CurrentContextModel } from '../../models/current-context.model';
import { DatabaseObjectModel } from '../../models/database-object.model'

@Component({
  selector: 'app-db-content',
  templateUrl: './db-content.component.html',
  styleUrls: ['./db-content.component.css']
})

/**
 * Content to display in main body
 */
export class DbContentComponent implements OnInit {
  public endpointList: EndpointListModel;
  public currentEndpoint: EndpointModel;
  public currentContext: CurrentContextModel;
  public objectDetails: DatabaseObjectModel;

  public schemaColumns: string[] = ['type', 'count'];

  constructor(
    private restService: RestService,
    private state: StateService) { }

  processContextChange(context: CurrentContextModel) {
    this.currentContext = context;
    if (context.endpoint && context.owner && context.objectType && context.objectName) {
      this.restService.getObjectDetails
      (context.endpoint, context.owner, context.objectType, context.objectName)
        .subscribe(result => { this.objectDetails = result; });
    }
  }

  ngOnInit() {
    this.state.endpoints.subscribe(
      endpoints => { this.endpointList = endpoints; }
    );
    this.state.currentEndpoint.subscribe(
      currentEndpoint => { this.currentEndpoint = currentEndpoint; }
    );
    this.state.currentContext.subscribe(
      context => { this.processContextChange(context); }
    );
  }

}