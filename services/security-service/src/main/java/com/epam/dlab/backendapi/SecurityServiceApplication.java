package com.epam.dlab.backendapi;

import com.epam.dlab.backendapi.resources.LoginResource;
import io.dropwizard.Application;
import io.dropwizard.setup.Environment;

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
public class SecurityServiceApplication extends Application<SecurityServiceApplicationConfiguration> {
    public static void main(String... args) throws Exception {
        new SecurityServiceApplication().run(args);
    }

    @Override
    public void run(SecurityServiceApplicationConfiguration securityServiceApplicationConfiguration, Environment environment) throws Exception {
        environment.jersey().register(new LoginResource());
    }
}
