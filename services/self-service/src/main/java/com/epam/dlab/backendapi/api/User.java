package com.epam.dlab.backendapi.api;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.bson.Document;

import java.util.Date;

/**
 * Copyright 2016 EPAM Systems, Inc.
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * http://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
public class User {
    @JsonProperty
    private String login;
    @JsonProperty
    private String password;
    private Date date = new Date();

    public User(String login, String password) {
        this.login = login;
        this.password = password;
    }

    @JsonIgnore
    public Document getDocument() {
        return new Document("login", login)
                .append("timestamp", date);
    }
}
