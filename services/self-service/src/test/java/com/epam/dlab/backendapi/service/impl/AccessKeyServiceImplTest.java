package com.epam.dlab.backendapi.service.impl;

import com.epam.dlab.UserInstanceStatus;
import com.epam.dlab.auth.UserInfo;
import com.epam.dlab.backendapi.dao.KeyDAO;
import com.epam.dlab.backendapi.domain.RequestId;
import com.epam.dlab.backendapi.util.RequestBuilder;
import com.epam.dlab.dto.base.edge.EdgeInfo;
import com.epam.dlab.dto.base.keyload.UploadFile;
import com.epam.dlab.dto.keyload.KeyLoadStatus;
import com.epam.dlab.dto.keyload.UserKeyDTO;
import com.epam.dlab.exceptions.DlabException;
import com.epam.dlab.rest.client.RESTService;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.mockito.Mockito.*;

@RunWith(MockitoJUnitRunner.class)
public class AccessKeyServiceImplTest {

	private final String USER = "test";
	private final String TOKEN = "token";

	private UserInfo userInfo;

	@Mock
	private KeyDAO keyDAO;
	@Mock
	private RESTService provisioningService;
	@Mock
	private RequestBuilder requestBuilder;
	@Mock
	private RequestId requestId;

	@InjectMocks
	private AccessKeyServiceImpl accessKeyService;

	@Rule
	public ExpectedException expectedException = ExpectedException.none();

	@Before
	public void setUp() {
		userInfo = getUserInfo();
	}

	@Test
	public void getUserKeyStatus() {
		when(keyDAO.findKeyStatus(anyString())).thenReturn(KeyLoadStatus.SUCCESS);

		KeyLoadStatus keyLoadStatus = accessKeyService.getUserKeyStatus(USER);
		assertEquals(KeyLoadStatus.SUCCESS, keyLoadStatus);

		verify(keyDAO).findKeyStatus(USER);
		verifyNoMoreInteractions(keyDAO);
	}

	@Test
	public void getUserKeyStatusWithException() {
		doThrow(new DlabException("Some message")).when(keyDAO).findKeyStatus(anyString());

		KeyLoadStatus keyLoadStatus = accessKeyService.getUserKeyStatus(USER);
		assertEquals(KeyLoadStatus.ERROR, keyLoadStatus);

		verify(keyDAO).findKeyStatus(USER);
		verifyNoMoreInteractions(keyDAO);
	}

	@Test
	public void uploadKey() {
		doNothing().when(keyDAO).insertKey(anyString(), anyString());

		UploadFile uploadFile = mock(UploadFile.class);
		when(requestBuilder.newEdgeKeyUpload(any(UserInfo.class), anyString())).thenReturn(uploadFile);

		String expectedUuid = "someUuid";
		when(provisioningService.post(anyString(), anyString(), any(UploadFile.class), any())).thenReturn
				(expectedUuid);
		when(requestId.put(anyString(), anyString())).thenReturn(expectedUuid);

		String keyContent = "keyContent";
		String actualUuid = accessKeyService.uploadKey(userInfo, keyContent);
		assertNotNull(actualUuid);
		assertEquals(expectedUuid, actualUuid);

		verify(keyDAO).insertKey(USER, keyContent);
		verify(requestBuilder).newEdgeKeyUpload(userInfo, keyContent);
		verify(provisioningService).post("infrastructure/edge/create", TOKEN, uploadFile, String.class);
		verify(requestId).put(USER, expectedUuid);
		verifyNoMoreInteractions(keyDAO, requestBuilder, provisioningService, requestId);
	}


	@Test
	public void uploadKeyWithException() {
		doNothing().when(keyDAO).insertKey(anyString(), anyString());
		doThrow(new RuntimeException()).when(requestBuilder).newEdgeKeyUpload(any(UserInfo.class), anyString());

		expectedException.expect(RuntimeException.class);

		doNothing().when(keyDAO).deleteKey(anyString());
		expectedException.expect(DlabException.class);
		expectedException.expectMessage("Could not upload the key and create EDGE node: ");

		accessKeyService.uploadKey(userInfo, "someKeyContent");
	}

	@Test
	public void recoverEdge() {
		EdgeInfo edgeInfo = new EdgeInfo();
		edgeInfo.setId("someId");
		edgeInfo.setEdgeStatus("failed");
		when(keyDAO.getEdgeInfo(anyString())).thenReturn(edgeInfo);

		UserKeyDTO userKeyDTO = new UserKeyDTO();
		userKeyDTO.withStatus("someStatus");
		userKeyDTO.withContent("someContent");
		when(keyDAO.fetchKey(anyString(), any(KeyLoadStatus.class))).thenReturn(userKeyDTO);

		edgeInfo.setEdgeStatus("terminated");
		edgeInfo.setInstanceId(null);

		doNothing().when(keyDAO).updateEdgeInfo(anyString(), any(EdgeInfo.class));

		UploadFile uploadFile = mock(UploadFile.class);
		when(requestBuilder.newEdgeKeyUpload(any(UserInfo.class), anyString())).thenReturn(uploadFile);

		String expectedUuid = "someUuid";
		when(provisioningService.post(anyString(), anyString(), any(UploadFile.class), any())).thenReturn
				(expectedUuid);
		when(requestId.put(anyString(), anyString())).thenReturn(expectedUuid);

		String actualUuid = accessKeyService.recoverEdge(userInfo);
		assertNotNull(actualUuid);
		assertEquals(expectedUuid, actualUuid);

		verify(keyDAO).getEdgeInfo(USER);
		verify(keyDAO).fetchKey(USER, KeyLoadStatus.SUCCESS);
		verify(keyDAO).updateEdgeInfo(USER, edgeInfo);

		verify(requestBuilder).newEdgeKeyUpload(userInfo, userKeyDTO.getContent());
		verify(provisioningService).post("infrastructure/edge/create", TOKEN, uploadFile, String.class);
		verify(requestId).put(USER, expectedUuid);
		verifyNoMoreInteractions(keyDAO, requestBuilder, provisioningService, requestId);
	}

	@Test
	public void recoverEdgeWithExceptionInGetEdgeInfoMethod() {
		EdgeInfo edgeInfo = new EdgeInfo();
		edgeInfo.setId("someId");
		edgeInfo.setEdgeStatus("running");
		when(keyDAO.getEdgeInfo(anyString())).thenReturn(edgeInfo);

		expectedException.expect(DlabException.class);
		expectedException.expectMessage("Could not create EDGE node because the status of instance is running");

		doNothing().when(keyDAO).updateEdgeStatus(anyString(), anyString());

		expectedException.expect(DlabException.class);
		expectedException.expectMessage("Could not upload the key and create EDGE node:");

		accessKeyService.recoverEdge(userInfo);

		verify(keyDAO).getEdgeInfo(USER);
		verify(keyDAO).updateEdgeStatus(USER, UserInstanceStatus.FAILED.toString());
		verifyNoMoreInteractions(keyDAO);
		verifyZeroInteractions(requestBuilder, provisioningService, requestId);
	}

	@Test
	public void recoverEdgeWithExceptionInFetchKeyMethod() {
		EdgeInfo edgeInfo = new EdgeInfo();
		edgeInfo.setId("someId");
		edgeInfo.setEdgeStatus("failed");
		when(keyDAO.getEdgeInfo(anyString())).thenReturn(edgeInfo);

		UserKeyDTO userKeyDTO = new UserKeyDTO();
		userKeyDTO.withStatus("someStatus");
		userKeyDTO.withContent("someContent");
		doThrow(new DlabException(String.format("Key of user %s with status %s not found", USER, KeyLoadStatus
				.SUCCESS)))
				.when(keyDAO).fetchKey(anyString(), eq(KeyLoadStatus.SUCCESS));

		doNothing().when(keyDAO).updateEdgeStatus(anyString(), anyString());

		expectedException.expect(DlabException.class);
		expectedException.expectMessage("Could not upload the key and create EDGE node: ");

		accessKeyService.recoverEdge(userInfo);

		verify(keyDAO).getEdgeInfo(USER);
		verify(keyDAO).fetchKey(USER, KeyLoadStatus.SUCCESS);
		verify(keyDAO).updateEdgeStatus(USER, UserInstanceStatus.FAILED.toString());
		verifyNoMoreInteractions(keyDAO);
		verifyZeroInteractions(requestBuilder, provisioningService, requestId);
	}

	private UserInfo getUserInfo() {
		return new UserInfo(USER, TOKEN);
	}

}
