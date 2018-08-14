/*
 * **************************************************************************
 *
 * Copyright (c) 2018, EPAM SYSTEMS INC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * ***************************************************************************
 */

package com.epam.dlab.backendapi.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
@Getter
public class MavenSearchArtifactResponse {

	@JsonProperty("response")
	private Response response;

	public void setResponse(Response response) {
		this.response = response;
	}

	public int getArtifactCount() {
		return response.artifactCount;
	}

	public List<Response.Artifact> getArtifacts() {
		return response.artifacts;
	}

	@JsonIgnoreProperties(ignoreUnknown = true)
	public static class Response {
		@JsonProperty("numFound")
		private int artifactCount;
		@JsonProperty("docs")
		private List<Artifact> artifacts;

		public void setArtifacts(List<Artifact> artifacts) {
			this.artifacts = artifacts;
		}

		@JsonIgnoreProperties(ignoreUnknown = true)
		public static class Artifact {
			private String id;
			@JsonProperty("v")
			private String version;

			public String getId() {
				return id;
			}

			public void setId(String id) {
				this.id = id;
			}

			public String getVersion() {
				return version;
			}

			public void setVersion(String version) {
				this.version = version;
			}
		}
	}

}
