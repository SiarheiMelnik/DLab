/***************************************************************************

Copyright (c) 2016, EPAM SYSTEMS INC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

****************************************************************************/
/* tslint:disable:no-empty */

import { Component, ViewChild, OnInit } from '@angular/core';
import { UserResourceService } from '../../core/services';
import { ResourcesGridRowModel, FilterConfigurationModel, CreateResourceModel } from './';
import { ConfirmationDialogType } from '../../shared';
import { SortUtil } from '../../core/util';

@Component({
  moduleId: module.id,
  selector: 'resources-grid',
  templateUrl: 'resources-grid.component.html',
  styleUrls: ['./resources-grid.component.css']
})

export class ResourcesGridComponent implements OnInit {

  environments: Array<ResourcesGridRowModel>;
  filteredEnvironments: Array<ResourcesGridRowModel> = [];
  filterConfiguration: FilterConfigurationModel;
  filterForm: FilterConfigurationModel = new FilterConfigurationModel('', [], [], [], '');
  model = new CreateResourceModel('', '');
  notebookName: string;
  isOutscreenDropdown: boolean;
  collapseFilterRow: boolean = false;
  filtering: boolean = false;
  activeFiltering: boolean = false;
  healthStatus: string = '';

  @ViewChild('computationalResourceModal') computationalResourceModal;
  @ViewChild('confirmationDialog') confirmationDialog;
  @ViewChild('detailDialog') detailDialog;
  @ViewChild('costDetailsDialog') costDetailsDialog;
  @ViewChild('installLibs') installLibraries;


  public filteringColumns: Array<any> = [
    { title: 'Environment name', name: 'name', className: 'th_name', filtering: {} },
    { title: 'Status', name: 'statuses', className: 'th_status', filtering: {} },
    { title: 'Shape', name: 'shapes', className: 'th_shape', filtering: {} },
    { title: 'Computational resources', name: 'resources', className: 'th_resources', filtering: {} },
    { title: 'Cost', name: 'cost', className: 'th_cost' },
    { title: 'Actions', className: 'th_actions' }
  ];

  constructor(
    private userResourceService: UserResourceService
  ) { }

  ngOnInit(): void {
    this.buildGrid();
  }

  toggleFilterRow(): void {
    this.collapseFilterRow = !this.collapseFilterRow;
  }

  getDefaultFilterConfiguration(): void {
    const data: Array<ResourcesGridRowModel> = this.environments;
    const shapes = [], statuses = [], resources = [];

    data.forEach((item: any) => {
      if (shapes.indexOf(item.shape) === -1)
        shapes.push(item.shape);
      if (statuses.indexOf(item.status) === -1)
        statuses.push(item.status);
        statuses.sort(SortUtil.statusSort);

      item.resources.forEach((resource: any) => {
        if (resources.indexOf(resource.status) === -1)
          resources.push(resource.status);
          resources.sort(SortUtil.statusSort);
      });
    });

    this.filterConfiguration = new FilterConfigurationModel('', statuses, shapes, resources, '');
  }

  applyFilter_btnClick(config: FilterConfigurationModel) {
    this.filtering = true;

    // let filteredData: Array<ResourcesGridRowModel> = this.environments.map(env => (<any>Object).assign({}, env));
    let filteredData: Array<ResourcesGridRowModel> = this.environments.map(env => (<any>Object).create(env));
    const containsStatus = (list, selectedItems) => {
      return list.filter((item: any) => { if (selectedItems.indexOf(item.status) !== -1) return item; });
    };

    filteredData = filteredData.filter((item: any) => {
      const isName = item.name.toLowerCase().indexOf(config.name.toLowerCase()) !== -1;
      const isStatus = config.statuses.length > 0 ? (config.statuses.indexOf(item.status) !== -1) : (config.type !== 'active');
      const isShape = config.shapes.length > 0 ? (config.shapes.indexOf(item.shape) !== -1) : true;

      const modifiedResources = containsStatus(item.resources, config.resources);
      let isResources = config.resources.length > 0 ? (modifiedResources.length > 0) : true;

      if (config.resources.length > 0 && modifiedResources.length > 0) { item.resources = modifiedResources; }
      if (config.resources.length === 0 && config.type === 'active' ||
        modifiedResources.length >= 0 && config.resources.length > 0 && config.type === 'active') {
        item.resources = modifiedResources;
        isResources = true;
      }

      return isName && isStatus && isShape && isResources;
    });

    this.updateUserPreferences(config);
    config.type = '';

    this.filteredEnvironments = filteredData;
  }

  showActiveInstances(): void {
    const filteredData = (<any>Object).assign({}, this.filterConfiguration);
    filteredData.type = 'active';

    for (const index in filteredData) {
      if (filteredData[index] instanceof Array)
        filteredData[index] = filteredData[index].filter((item: string) => {
          return (item !== 'failed' && item !== 'terminated' && item !== 'terminating');
        });
      if (index === 'shapes') { filteredData[index] = []; }
    }

    this.filterForm = this.loadUserPreferences(filteredData);
    this.applyFilter_btnClick(this.filterForm);
    this.buildGrid();
  }

  aliveStatuses(сonfig): void {
    for (const index in this.filterConfiguration) {
      if (сonfig[index] && сonfig[index] instanceof Array)
         сonfig[index] = сonfig[index].filter(item => this.filterConfiguration[index].includes(item));
    }

    return сonfig;
  }

  onUpdate($event) {
    this.filterForm[$event.type] = $event.model;
  }

  resetFilterConfigurations(): void {
    this.filterForm.resetConfigurations();
    this.updateUserPreferences(this.filterForm);
    this.buildGrid();
  }

  buildGrid(): void {
    this.userResourceService.getUserProvisionedResources()
      .subscribe((result) => {
        this.environments = this.loadEnvironments(result);
        this.getDefaultFilterConfiguration();

        (this.environments.length) ? this.getUserPreferences() : this.filteredEnvironments = [];
      });
  }

  containsNotebook(notebook_name: string): boolean {
    if (notebook_name)
      for (let index = 0; index < this.environments.length; index++)
        if (notebook_name.toLowerCase() === this.environments[index].name.toString().toLowerCase())
          return true;

    return false;
  }

  loadEnvironments(exploratoryList: Array<any>): Array<ResourcesGridRowModel> {
    if (exploratoryList) {
      return exploratoryList.map((value) => {
        return new ResourcesGridRowModel(value.exploratory_name,
          value.template_name,
          value.image,
          value.status,
          value.shape,
          value.computational_resources,
          value.up_time,
          value.exploratory_url,
          value.edge_node_ip,
          value.exploratory_user,
          value.exploratory_pass,
          value.user_own_bicket_name,
          value.error_message,
          value.cost,
          value.currency_code,
          value.billing,
          value.libs);
      });
    }
  }

  getUserPreferences(): void {
    this.userResourceService.getUserPreferences()
      .subscribe((result) => {

        this.isActiveFilter(result);
        this.filterForm = this.loadUserPreferences(this.aliveStatuses(result));

        this.applyFilter_btnClick(this.filterForm);
      }, (error) => {
        // FIXME: to avoid SyntaxError: in case of empty database
        this.applyFilter_btnClick(this.filterForm);
        console.log('GET USER PREFERENCES ERROR', error);
      });
  }

  loadUserPreferences(config): FilterConfigurationModel {
    return new FilterConfigurationModel(config.name, config.statuses, config.shapes, config.resources, config.type);
  }

  updateUserPreferences(filterConfiguration: FilterConfigurationModel): void {
    this.userResourceService.updateUserPreferences(filterConfiguration)
      .subscribe((result) => { },
      (error) => {
        console.log('UPDATE USER PREFERENCES ERROR ', error);
      });
  }

  isActiveFilter(filterConfig): void {
    this.activeFiltering = false;

    for (const index in filterConfig)
      if (filterConfig[index].length)
        this.activeFiltering = true;
  }

  printDetailEnvironmentModal(data): void {
    this.detailDialog.open({ isFooter: false }, data);
  }

  printCostDetails(data): void {
    this.costDetailsDialog.open({ isFooter: false }, data);
  }

  exploratoryAction(data, action: string) {

    if (action === 'deploy') {
      this.notebookName = data.name;
      this.computationalResourceModal.open({ isFooter: false }, data);
    } else if (action === 'run') {
      this.userResourceService
        .runExploratoryEnvironment({ notebook_instance_name: data.name })
        .subscribe((result) => {
          console.log('startUsernotebook result: ', result);
          this.buildGrid();
        });
    } else if (action === 'stop') {
      this.confirmationDialog.open({ isFooter: false }, data, ConfirmationDialogType.StopExploratory);
    } else if (action === 'terminate') {
      this.confirmationDialog.open({ isFooter: false }, data, ConfirmationDialogType.TerminateExploratory);
    } else if (action === 'install') {
      this.installLibraries.open({ isFooter: false }, data);
    }
  }

  dropdownPosition($event): void {
    const contentHeight = document.body.offsetHeight > window.outerHeight ? document.body.offsetHeight : window.outerHeight;
    this.isOutscreenDropdown = $event.pageY + 215 > contentHeight ? true : false;
  }
}