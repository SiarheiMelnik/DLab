package com.epam.dlab.backendapi.api.form;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Created by Maksym_Pendyshchuk on 10/20/2016.
 */
public class ExploratoryTerminateFormDTO {
    @JsonProperty("notebook_instance_name")
    private String notebookInstanceName;

    public String getNotebookInstanceName() {
        return notebookInstanceName;
    }

}
